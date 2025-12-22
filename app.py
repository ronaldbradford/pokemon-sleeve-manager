import os
import json
import hashlib
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import imagehash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'collection'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['DATABASE'] = 'collection_db.json'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_database():
    """Load the collection database"""
    if os.path.exists(app.config['DATABASE']):
        with open(app.config['DATABASE'], 'r') as f:
            return json.load(f)
    return {'images': []}

def save_database(db):
    """Save the collection database"""
    with open(app.config['DATABASE'], 'w') as f:
        json.dump(db, f, indent=2)

def order_points(pts):
    """Order points in clockwise order: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")
    
    # Sum and diff to find corners
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    
    rect[0] = pts[np.argmin(s)]  # top-left has smallest sum
    rect[2] = pts[np.argmax(s)]  # bottom-right has largest sum
    rect[1] = pts[np.argmin(diff)]  # top-right has smallest difference
    rect[3] = pts[np.argmax(diff)]  # bottom-left has largest difference
    
    return rect

def perspective_transform(image, pts):
    """Apply perspective transform to straighten the image"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    # Calculate width
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    # Calculate height
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    # Destination points
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    
    # Compute perspective transform matrix and apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warped

def auto_crop_sleeve(image_path):
    """
    Automatically detect and crop the sleeve from a solid background.
    Returns the path to the processed image.
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return image_path, False  # Return original if can't read
    
    original = img.copy()
    height, width = img.shape[:2]
    
    # Convert to different color spaces for better detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Try multiple edge detection approaches
    edges1 = cv2.Canny(blurred, 30, 150)
    edges2 = cv2.Canny(blurred, 50, 200)
    
    # Combine edge detection results
    edges = cv2.bitwise_or(edges1, edges2)
    
    # Dilate edges to close gaps
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return image_path, False
    
    # Find the largest contour (likely the sleeve)
    largest_contour = max(contours, key=cv2.contourArea)
    contour_area = cv2.contourArea(largest_contour)
    image_area = width * height
    
    # Check if contour is significant (at least 10% of image)
    if contour_area < image_area * 0.1:
        return image_path, False
    
    # Approximate the contour to a polygon
    peri = cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
    
    # If we have 4 corners, apply perspective transform
    if len(approx) == 4:
        pts = approx.reshape(4, 2)
        warped = perspective_transform(original, pts)
        
        # Save the processed image
        processed_path = image_path.replace('.', '_processed.')
        cv2.imwrite(processed_path, warped)
        return processed_path, True
    
    # Otherwise, just crop to bounding rectangle
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Add small padding
    padding = 10
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(width - x, w + 2 * padding)
    h = min(height - y, h + 2 * padding)
    
    # Crop the image
    cropped = original[y:y+h, x:x+w]
    
    # Save the processed image
    processed_path = image_path.replace('.', '_processed.')
    cv2.imwrite(processed_path, cropped)
    return processed_path, True

def compute_image_hash(image_path):
    """Compute perceptual hash for duplicate detection"""
    img = Image.open(image_path)
    # Use difference hash - good for finding duplicates
    dhash = str(imagehash.dhash(img))
    # Also compute average hash for additional comparison
    ahash = str(imagehash.average_hash(img))
    return {'dhash': dhash, 'ahash': ahash}

def find_similar_images(target_hashes, db, threshold=5):
    """Find similar images in the database using hamming distance"""
    similar = []
    target_dhash = imagehash.hex_to_hash(target_hashes['dhash'])
    target_ahash = imagehash.hex_to_hash(target_hashes['ahash'])
    
    for img in db['images']:
        stored_dhash = imagehash.hex_to_hash(img['hashes']['dhash'])
        stored_ahash = imagehash.hex_to_hash(img['hashes']['ahash'])
        
        # Calculate hamming distance (lower = more similar)
        dhash_dist = target_dhash - stored_dhash
        ahash_dist = target_ahash - stored_ahash
        
        # If either hash is very similar, consider it a match
        if dhash_dist <= threshold or ahash_dist <= threshold:
            similar.append({
                'id': img['id'],
                'filename': img['filename'],
                'distance': min(dhash_dist, ahash_dist),
                'tags': img['tags']
            })
    
    return sorted(similar, key=lambda x: x['distance'])

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/collection', methods=['GET'])
def get_collection():
    """Get all images in the collection"""
    db = load_database()
    search_query = request.args.get('search', '').lower()
    tag_filter = request.args.get('tag', '').lower()
    
    images = db['images']
    
    # Filter by search query
    if search_query:
        images = [img for img in images if 
                  search_query in img.get('name', '').lower() or 
                  search_query in img.get('description', '').lower() or
                  any(search_query in tag.lower() for tag in img.get('tags', []))]
    
    # Filter by tag
    if tag_filter:
        images = [img for img in images if tag_filter in [t.lower() for t in img.get('tags', [])]]
    
    return jsonify({'images': images, 'total': len(images)})

@app.route('/api/process-image', methods=['POST'])
def process_image():
    """Process an image to crop and straighten it"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Save file temporarily
    temp_filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_process_' + temp_filename)
    file.save(temp_path)
    
    try:
        # Process the image
        processed_path, success = auto_crop_sleeve(temp_path)
        
        if success and processed_path != temp_path:
            # Read the processed image and convert to base64 for preview
            with open(processed_path, 'rb') as f:
                import base64
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Determine file extension
            ext = processed_path.split('.')[-1]
            img_data_url = f"data:image/{ext};base64,{img_data}"
            
            # Clean up temp files
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(processed_path):
                os.remove(processed_path)
            
            return jsonify({
                'success': True,
                'processed': True,
                'image_data': img_data_url,
                'message': 'Image successfully cropped and straightened!'
            })
        else:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify({
                'success': True,
                'processed': False,
                'message': 'Could not auto-detect sleeve edges. Image will be used as-is.'
            })
    
    except Exception as e:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload a new image to the collection"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Get metadata
    name = request.form.get('name', '')
    description = request.form.get('description', '')
    tags = request.form.get('tags', '')
    tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    auto_process = request.form.get('auto_process', 'true').lower() == 'true'
    
    # Save file temporarily to process
    temp_filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_' + temp_filename)
    file.save(temp_path)
    
    try:
        # Auto-process if requested
        processed_path = temp_path
        was_processed = False
        
        if auto_process:
            processed_path, was_processed = auto_crop_sleeve(temp_path)
        
        # Compute image hash on the final image
        image_hashes = compute_image_hash(processed_path)
        
        # Check for duplicates
        db = load_database()
        similar = find_similar_images(image_hashes, db, threshold=5)
        
        if similar and similar[0]['distance'] <= 3:
            # Very similar image found
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if was_processed and os.path.exists(processed_path):
                os.remove(processed_path)
            return jsonify({
                'duplicate': True,
                'similar': similar[0],
                'message': 'This image appears to already be in your collection!'
            }), 409
        
        # Generate unique ID and filename
        image_id = hashlib.md5(f"{datetime.now().isoformat()}{temp_filename}".encode()).hexdigest()[:12]
        ext = temp_filename.rsplit('.', 1)[1].lower()
        new_filename = f"{image_id}.{ext}"
        new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        
        # Move processed file to permanent location
        if os.path.exists(processed_path):
            os.rename(processed_path, new_path)
        
        # Clean up temp file if it's different from processed
        if temp_path != processed_path and os.path.exists(temp_path):
            os.remove(temp_path)
        
        # Add to database
        image_entry = {
            'id': image_id,
            'filename': new_filename,
            'original_filename': file.filename,
            'name': name,
            'description': description,
            'tags': tags_list,
            'hashes': image_hashes,
            'added_date': datetime.now().isoformat(),
            'file_size': os.path.getsize(new_path),
            'was_auto_processed': was_processed
        }
        
        db['images'].append(image_entry)
        save_database(db)
        
        message = 'Image added successfully!'
        if was_processed:
            message += ' (Auto-cropped and straightened)'
        
        return jsonify({
            'success': True,
            'image': image_entry,
            'message': message
        }), 201
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if 'processed_path' in locals() and processed_path != temp_path and os.path.exists(processed_path):
            os.remove(processed_path)
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-duplicate', methods=['POST'])
def check_duplicate():
    """Check if an uploaded image is a duplicate"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    auto_process = request.form.get('auto_process', 'true').lower() == 'true'
    
    # Save file temporarily
    temp_filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'check_' + temp_filename)
    file.save(temp_path)
    
    try:
        # Auto-process if requested
        processed_path = temp_path
        was_processed = False
        
        if auto_process:
            processed_path, was_processed = auto_crop_sleeve(temp_path)
        
        # Compute hash
        image_hashes = compute_image_hash(processed_path)
        
        # Find similar images
        db = load_database()
        similar = find_similar_images(image_hashes, db, threshold=10)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if was_processed and os.path.exists(processed_path):
            os.remove(processed_path)
        
        if similar:
            message = 'Similar images found!'
            if was_processed:
                message += ' (Image was auto-processed for better comparison)'
            
            return jsonify({
                'is_duplicate': similar[0]['distance'] <= 5,
                'similar_images': similar[:5],
                'message': message,
                'was_processed': was_processed
            })
        else:
            return jsonify({
                'is_duplicate': False,
                'similar_images': [],
                'message': 'No similar images found in your collection.',
                'was_processed': was_processed
            })
    
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/<image_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_image(image_id):
    """Get, update, or delete a specific image"""
    db = load_database()
    image = next((img for img in db['images'] if img['id'] == image_id), None)
    
    if not image:
        return jsonify({'error': 'Image not found'}), 404
    
    if request.method == 'GET':
        return jsonify(image)
    
    elif request.method == 'PUT':
        # Update metadata
        data = request.json
        if 'name' in data:
            image['name'] = data['name']
        if 'description' in data:
            image['description'] = data['description']
        if 'tags' in data:
            image['tags'] = data['tags']
        
        image['modified_date'] = datetime.now().isoformat()
        save_database(db)
        
        return jsonify({'success': True, 'image': image})
    
    elif request.method == 'DELETE':
        # Delete image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filename'])
        if os.path.exists(image_path):
            os.remove(image_path)
        
        db['images'] = [img for img in db['images'] if img['id'] != image_id]
        save_database(db)
        
        return jsonify({'success': True, 'message': 'Image deleted'})

@app.route('/api/tags', methods=['GET'])
def get_all_tags():
    """Get all unique tags in the collection"""
    db = load_database()
    tags = set()
    for img in db['images']:
        tags.update(img.get('tags', []))
    
    return jsonify({'tags': sorted(list(tags))})

@app.route('/collection/<filename>')
def serve_image(filename):
    """Serve images from the collection folder"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/gallery')
def gallery_view():
    """Simple gallery view - images only"""
    return render_template('gallery.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
