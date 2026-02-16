# Using iStripper Model Content

This guide shows you how to use your actual iStripper installation's model content (videos and images) with Thermalright LCD Control, instead of just window capture.

## Overview

The application can now detect and access your iStripper model library, allowing you to:
- Use model videos directly as backgrounds
- Display model preview images
- Create playlists from your collection
- Rotate through different models automatically

## Quick Start

### 1. Automatic Detection

The system automatically detects your iStripper content during installation. You can verify this with:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()

# Detect installation
if manager.detect_installation():
    print(f"iStripper found: {manager.installation_path}")
    
    # Detect content directory
    content_dir = manager.detect_content_directory()
    if content_dir:
        print(f"Content directory: {content_dir}")
        
        # List models
        models = manager.list_model_directories()
        print(f"Found {len(models)} models")
    else:
        print("No model content found (install models in iStripper)")
else:
    print("iStripper not installed")
```

### 2. List Your Models

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()

# Get all model directories
models = manager.list_model_directories()

print(f"You have {len(models)} models installed:")
for i, model in enumerate(models[:20], 1):  # Show first 20
    print(f"{i:2d}. {model.name}")
```

### 3. Access Model Media Files

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()
models = manager.list_model_directories()

if models:
    # Get media files from first model
    first_model = models[0]
    media_files = manager.get_model_media_files(first_model)
    
    print(f"Model {first_model.name} contains:")
    for file in media_files:
        print(f"  - {file.name} ({file.stat().st_size / 1024 / 1024:.1f} MB)")
```

## Usage Scenarios

### Scenario 1: Single Model Video Background

Use a specific model's video as your LCD background:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

# Setup
manager = IStripperManager()
manager.detect_installation()
models = manager.list_model_directories()

# Select a model (e.g., first one)
selected_model = models[0]

# Get videos from this model
videos = manager.get_model_media_files(selected_model, extensions=['.mp4'])

if videos:
    # Use the first video
    video_path = str(videos[0])
    print(f"Using: {video_path}")
    
    # Configure your display to use this video
    # Update your config YAML:
    # display:
    #   background:
    #     type: video
    #     path: {video_path}
```

### Scenario 2: Random Model Selection

Randomly pick a model each time:

```python
import random
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()

# Get all models with videos
all_media = manager.get_all_model_media(extensions=['.mp4'])

if all_media:
    # Pick random model
    model_name = random.choice(list(all_media.keys()))
    model_videos = all_media[model_name]
    
    # Pick random video
    video = random.choice(model_videos)
    
    print(f"Selected model: {model_name}")
    print(f"Video: {video.name}")
    print(f"Path: {video}")
```

### Scenario 3: Create Model Playlist

Create a playlist rotating through multiple models:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()

# Get videos from first 5 models
models = manager.list_model_directories()[:5]
playlist = []

for model in models:
    videos = manager.get_model_media_files(model, extensions=['.mp4'])
    if videos:
        # Add first video from each model
        playlist.append(str(videos[0]))

print(f"Created playlist with {len(playlist)} videos:")
for i, video_path in enumerate(playlist, 1):
    print(f"{i}. {video_path}")

# Use with image_collection background type:
# display:
#   background:
#     type: image_collection
#     path: /path/to/playlist/directory
```

### Scenario 4: Use Preview Images

Use model preview images for faster loading:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()
models = manager.list_model_directories()

# Get images instead of videos
images = []
for model in models[:10]:  # First 10 models
    media = manager.get_model_media_files(model, extensions=['.jpg', '.png'])
    if media:
        images.append(str(media[0]))

print(f"Found {len(images)} preview images")
```

### Scenario 5: Filter by File Size

Only use videos within a certain size range:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()

all_media = manager.get_all_model_media(extensions=['.mp4'], limit=20)

suitable_videos = []
for model_name, videos in all_media.items():
    for video in videos:
        # Only videos between 10MB and 100MB
        size_mb = video.stat().st_size / 1024 / 1024
        if 10 <= size_mb <= 100:
            suitable_videos.append((model_name, video, size_mb))

print(f"Found {len(suitable_videos)} suitable videos:")
for model, video, size in suitable_videos[:10]:
    print(f"  {model}/{video.name} ({size:.1f} MB)")
```

## Configuration Examples

### Example 1: Static Model Video

Edit your config YAML (e.g., `config_320x240.yaml`):

```yaml
display:
  background:
    type: video
    path: "C:/Program Files/iStripper/DATA/0001/video1.mp4"
  # ... rest of config
```

### Example 2: Image Collection from Models

Create a directory with symlinks or copies of model previews, then:

```yaml
display:
  background:
    type: image_collection
    path: "./model_previews"
  # ... rest of config
```

### Example 3: Window Capture (Original Method)

If you prefer window capture, that still works:

```yaml
display:
  background:
    type: window_capture
    path: ""
  window_title: "iStripper"
  capture_fps: 30
  scale_factor: 1.5
```

## API Reference

### IStripperManager Methods

#### `detect_content_directory()`
Detects the iStripper content directory containing models.

**Returns:** `Path` object or `None`

**Example:**
```python
content_dir = manager.detect_content_directory()
```

#### `get_content_directory(auto_detect=True)`
Gets the cached content directory, optionally auto-detecting if not cached.

**Returns:** `Path` object or `None`

#### `list_model_directories()`
Lists all model directories in the content folder.

**Returns:** List of `Path` objects

**Example:**
```python
models = manager.list_model_directories()
# Returns: [Path('DATA/0001'), Path('DATA/0002'), ...]
```

#### `get_model_media_files(model_dir, extensions=None)`
Gets media files from a specific model directory.

**Parameters:**
- `model_dir`: Path to model directory
- `extensions`: List of file extensions (default: common video/image formats)

**Returns:** List of `Path` objects

**Example:**
```python
videos = manager.get_model_media_files(models[0], extensions=['.mp4'])
```

#### `get_all_model_media(extensions=None, limit=None)`
Gets all model media files organized by model.

**Parameters:**
- `extensions`: List of file extensions to include
- `limit`: Maximum number of models to process

**Returns:** Dictionary mapping model names to file lists

**Example:**
```python
all_media = manager.get_all_model_media(extensions=['.mp4'], limit=10)
# Returns: {'0001': [Path(...), ...], '0002': [...], ...}
```

## Troubleshooting

### Content Directory Not Found

**Symptom:** `detect_content_directory()` returns `None`

**Solutions:**
1. Verify iStripper is installed:
   ```python
   manager.detect_installation()
   print(manager.installation_path)
   ```

2. Check if models are installed in iStripper:
   - Open iStripper
   - Go to your model library
   - Download at least one model

3. Check common locations manually:
   - `C:\Program Files\iStripper\DATA`
   - `C:\Program Files (x86)\iStripper\DATA`
   - `D:\iStripper\DATA` (if installed on different drive)

4. Use Windows Explorer to locate the DATA folder:
   - Navigate to iStripper installation directory
   - Look for `DATA`, `Models`, or `Shows` folder

### No Media Files Found

**Symptom:** `list_model_directories()` returns empty list

**Possible Causes:**
- No models installed yet
- Models in non-standard location
- Permission issues

**Solution:**
```python
# Check if content directory exists
content_dir = manager.get_content_directory()
if content_dir:
    print(f"Content dir: {content_dir}")
    print(f"Exists: {content_dir.exists()}")
    print(f"Is directory: {content_dir.is_dir()}")
    
    # List contents
    try:
        items = list(content_dir.iterdir())
        print(f"Contains {len(items)} items")
        for item in items[:5]:
            print(f"  - {item.name} (dir: {item.is_dir()})")
    except Exception as e:
        print(f"Error: {e}")
```

### Models in Different Location

If iStripper stores models in a custom location:

1. Find the actual location using iStripper settings
2. Manually set the path:
   ```python
   from pathlib import Path
   manager.content_directory = Path("E:/MyVideos/iStripper/DATA")
   ```

3. Then use normally:
   ```python
   models = manager.list_model_directories()
   ```

## Advanced Usage

### Create Custom Background Selector

```python
import random
from pathlib import Path
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

class ModelBackgroundSelector:
    def __init__(self):
        self.manager = IStripperManager()
        self.manager.detect_installation()
        self.models = self.manager.list_model_directories()
        
    def get_random_video(self):
        """Get a random model video"""
        if not self.models:
            return None
        
        model = random.choice(self.models)
        videos = self.manager.get_model_media_files(model, extensions=['.mp4'])
        
        return str(random.choice(videos)) if videos else None
    
    def get_video_by_model_id(self, model_id):
        """Get video from specific model ID"""
        for model in self.models:
            if model.name == model_id:
                videos = self.manager.get_model_media_files(model, extensions=['.mp4'])
                return str(videos[0]) if videos else None
        return None
    
    def get_model_count(self):
        """Get total number of models"""
        return len(self.models)

# Usage
selector = ModelBackgroundSelector()
print(f"You have {selector.get_model_count()} models")

random_video = selector.get_random_video()
print(f"Random video: {random_video}")
```

### Monitor for New Models

```python
import time
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

def monitor_new_models(check_interval=60):
    """Monitor for newly installed models"""
    manager = IStripperManager()
    manager.detect_installation()
    
    known_models = set(m.name for m in manager.list_model_directories())
    print(f"Starting with {len(known_models)} models")
    
    while True:
        time.sleep(check_interval)
        
        current_models = set(m.name for m in manager.list_model_directories())
        new_models = current_models - known_models
        
        if new_models:
            print(f"New models detected: {new_models}")
            known_models = current_models
        
# Run in background thread
import threading
thread = threading.Thread(target=monitor_new_models, args=(60,), daemon=True)
thread.start()
```

## Tips

1. **Performance**: Use `limit` parameter when scanning many models:
   ```python
   # Only scan first 20 models
   media = manager.get_all_model_media(limit=20)
   ```

2. **File Types**: Specify exact extensions you need:
   ```python
   # Only MP4 videos
   videos = manager.get_model_media_files(model, extensions=['.mp4'])
   ```

3. **Caching**: Detection results are cached automatically:
   ```python
   # First call - performs detection
   content = manager.get_content_directory()
   
   # Subsequent calls - uses cache
   content = manager.get_content_directory()
   ```

4. **Error Handling**: Always check for None:
   ```python
   content_dir = manager.detect_content_directory()
   if content_dir:
       models = manager.list_model_directories()
   else:
       print("No content found - using fallback")
   ```

## See Also

- [iStripper Integration Guide](ISTRIPPER_INTEGRATION.md)
- [Windows 11 Setup](WINDOWS11_SETUP.md)
- Main README for basic setup

## Support

If you encounter issues:
1. Run the detection test:
   ```bash
   python -m thermalright_lcd_control.integrations.istripper_manager
   ```

2. Check the logs for details

3. Open an issue on GitHub with:
   - Your iStripper installation path
   - Content directory location
   - Number of models installed
   - Any error messages
