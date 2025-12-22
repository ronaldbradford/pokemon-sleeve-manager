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
./start.sh
```

#### Option B - Run directly (All platforms):
```bash
python app.py
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

### Gallery View
- **Clean visual display** - just images, no text
- **Click to enlarge** any sleeve to full size
- **ESC to close** full-size view
- **Perfect for browsing** your entire collection

---

## First Time Using the App?

### 1. **Add Your First Sleeve**
   - Click the "Add New" tab
   - Make sure "Auto-crop and straighten" is checked ✅
   - Upload an image of a Pokemon sleeve
   - Add a name, description, and tags
   - Click "Add to Collection"

### 2. **View Your Collection**
   - **Main View**: See all details, edit, search, filter
   - **Gallery View**: Click "🖼️ Gallery View" button for clean image-only display

### 3. **Check for Duplicates**
   - Click the "Check Duplicate" tab  
   - Upload an image
   - See if it matches anything in your collection

---

## Photography Tips

### Quick Setup
1. Place sleeve on **solid-colored surface** (orange, blue, white, etc.)
2. Ensure **good lighting**
3. Take photo from **directly above**
4. Make sure **all edges are visible**

### Best Background Colors
- ✅ Orange cutting mat (perfect!)
- ✅ Blue poster board
- ✅ White paper/table
- ✅ Green surface
- ✅ Any solid, contrasting color

---

## Troubleshooting

**Port 5000 already in use?**
Edit `app.py` and change the port number:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

**Permission denied on start.sh?**
```bash
chmod +x start.sh
```

**Auto-crop not working?**
- Try a more contrasting background color
- Ensure better lighting
- Make sure all sleeve edges are visible
- You can disable auto-processing if needed

**Need help?**
Check the full README.md for detailed documentation!

---

## File Structure

```
pokemon-sleeve-manager/
├── app.py              # Main application
├── templates/          
│   ├── index.html      # Main interface
│   └── gallery.html    # Gallery view
├── requirements.txt    # Dependencies
├── start.sh           # Startup script
└── README.md          # Full documentation
```

The app will automatically create these when you run it:
- `collection/` - Your uploaded images
- `collection_db.json` - Database of your sleeves

---

## Pro Tips

✅ **Take clear photos** with good lighting  
✅ **Use consistent tags** (lowercase, descriptive)  
✅ **Add descriptions** to help remember details  
✅ **Check duplicates** before adding new sleeves  
✅ **Use Gallery View** for quick visual browsing  
✅ **Backup** your `collection/` folder and `collection_db.json` regularly

Happy collecting! 🎴
