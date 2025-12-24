# Quick Start Guide 🚀

## Getting Started in 3 Easy Steps

### Step 1: Install Dependencies
Open a terminal in this directory and run:
```bash
pip install -r requirements.txt
```

Or if you're on Linux/Mac and get permission errors:
```bash
pip install -r requirements.txt --break-system-packages
```

### Step 2: Start the Server
#### Option A - Use the startup script (Linux/Mac):
```bash
./bin/start.sh
```

#### Option B - Run directly (All platforms):
```bash
python src/app.py
```


### Step 3: Open Your Browser
- **Main Collection**: http://localhost:5000
- **Gallery View**: http://localhost:5000/gallery

That's it! You're ready to start managing your Pokemon sleeve collection!

---

## 🆕 App Features

### Automatic Image Processing
The app automatically:
- ✅ Removes solid color backgrounds
- ✅ Crops to just the sleeve
- ✅ Straightens angled photos
- ✅ Creates perfect catalog images

### How to Use Auto-Processing

1. **Take a Photo**
   - Place sleeve on ANY solid-colored surface (orange, blue, white, green, etc.)
   - Snap a photo with your phone
   - Don't worry about perfect framing!

2. **Upload to the App**
   - Make sure "Auto-crop and straighten" is checked ✅
   - Upload your photo
   - Watch the app automatically process it!

3. **Preview & Add**
   - See the cleaned-up image preview
   - Add metadata if desired
   - Click "Add to Collection"

---

## First Time Using the App?

### Quick Photography Setup

**You'll Need:**
- 📱 Smartphone or camera
- 🎨 Solid-colored surface (cutting mat, poster board, colored paper)
- 💡 Good lighting (near window or even artificial light)

**Best Background Colors:**
- Orange (like in your example!) ✓
- Blue ✓
- White/Light colors ✓
- Green ✓
- Pink ✓

**Tips for Perfect Photos:**
1. Lay sleeve completely flat
2. Make sure all 4 corners are visible
3. Shoot from directly above
4. Keep your shadow out of the frame
5. Fill most of the photo with the sleeve

---

## Example Workflow

### Scenario 1: Building Your Collection

```
1. Gather 10-20 sleeves
2. Set up: Orange cutting mat + good light
3. Take photos (one per sleeve, ~30 seconds each)
4. Upload all with auto-processing ON
5. Add names/tags as you go
6. Done! Professional catalog in minutes
```

### Scenario 2: Checking Before You Buy

```
1. Find a sleeve online you want to buy
2. Save the seller's photo
3. Go to "Check Duplicate" tab
4. Upload with auto-processing ON
5. See instantly if you already own it!
6. Make informed decision
```

---

## Toggle Auto-Processing

You'll see checkboxes for auto-processing in two places:

1. **"Add New" Tab**: For adding sleeves to your collection
2. **"Check Duplicate" Tab**: For checking if you already have a sleeve

**When to Enable ✅:**
- Photo has a solid background
- Image needs straightening
- You want the best duplicate detection
- Quick phone photos

**When to Disable ❌:**
- Image is already perfectly cropped
- Professional product photos
- Sleeve has colors similar to background
- Artistic/display photos

---

## Troubleshooting

**Auto-crop didn't work?**
- Try a more contrasting background color
- Ensure better lighting with fewer shadows
- Make sure all edges are clearly visible
- Disable auto-processing and upload as-is

**Port 5000 already in use?**
Edit `src/app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

**OpenCV installation issues?**
```bash
pip install opencv-python --upgrade
```

---

## File Structure

```
pokemon-sleeve-manager/
├── src/
│   └── app.py                  # Main application with CV features
├── bin/
│   └── start.sh                # Startup script
├── templates/
│   ├── index.html              # Standard interface
│   └── index_enhanced.html     # Enhanced interface with processing
├── collection/                  # Your images (auto-created)
├── collection_db.json          # Database (auto-created)
├── requirements.txt            # Dependencies
├── README.md                   # Full documentation
└── QUICKSTART.md               # This file
```

---

## Pro Tips

### 📸 Photography Station Setup
1. Find a sturdy table near natural light
2. Place solid-color cutting mat or poster board
3. Keep your phone/camera ready
4. Shoot 10-20 sleeves in one session
5. Upload in batches

### 🏷️ Organization Strategy
- **By Pokemon**: pikachu, charizard, mewtwo
- **By Brand**: ultra-pro, dragon-shield, kmc
- **By Color**: red, blue, rainbow, holo
- **By Series**: base-set, xy, sword-shield
- **By Rarity**: rare, common, limited-edition

### 🎯 Workflow Efficiency
1. Photo session: Take all photos first
2. Batch upload: Upload 5-10 at a time
3. Tag later: Can edit tags anytime
4. Check regularly: Use duplicate checker when buying

---

## What Makes This Special?

**Traditional Method:**
1. Take photo
2. Edit in photo app
3. Crop manually
4. Straighten manually
5. Save
6. Upload
7. Repeat for each sleeve 😫

**With Enhanced App:**
1. Take photo (any background!)
2. Upload
3. Done! ✨

**Time Saved:** ~2-3 minutes per sleeve!

---

## Next Steps

1. ✅ Take a test photo on a solid background
2. ✅ Upload it with auto-processing enabled
3. ✅ See the magic happen!
4. ✅ Start building your collection

For detailed information, see **README_ENHANCED.md**

Happy collecting! 🎴
