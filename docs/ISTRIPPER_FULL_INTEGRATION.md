# iStripper Full Integration - Complete Model Library Access

This guide demonstrates the comprehensive iStripper integration that provides functionality similar to the iStripper interface itself, with full access to all models and subdirectories.

## Overview

The enhanced integration now provides:
- **Complete model library access** - Load all models just like iStripper does
- **Subdirectory traversal** - Access all content in clips, trailers, previews folders
- **Content organization** - Clips organized by type (clips/trailers/previews)
- **Comprehensive model info** - Size, file count, subdirectories, content types
- **Search and filter** - Find models by name, size, content type
- **Library statistics** - Overall library metrics and analytics

## Key Features

### 1. Load All Models (Like iStripper Interface)

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()

# Load all models - exactly like iStripper's library view
models = manager.list_model_directories()
print(f"Library contains {len(models)} models")

for i, model in enumerate(models[:20], 1):
    print(f"{i:3d}. {model.name}")
```

### 2. Access All Subdirectories Recursively

The integration automatically traverses all subdirectories, matching iStripper's structure:

```
Model_0001/
├── clips/          # Main show clips
│   ├── clip1.mp4
│   ├── clip2.mp4
│   └── clip3.mp4
├── trailers/       # Preview trailers
│   └── trailer.mp4
├── previews/       # Preview images
│   ├── preview1.jpg
│   └── preview2.jpg
└── other files...
```

```python
# Get ALL files from all subdirectories
model = models[0]
all_files = manager.get_model_media_files(model, recursive=True)

print(f"Model {model.name} contains {len(all_files)} files:")
for file in all_files:
    # Shows full path including subdirectories
    relative_path = file.relative_to(model)
    print(f"  {relative_path}")
```

### 3. Organized Content by Type

Get clips organized the same way iStripper organizes them:

```python
# Get clips organized by type (clips/trailers/previews)
clips = manager.get_model_clips(models[0])

print(f"Model {models[0].name} content:")
for content_type, files in clips.items():
    print(f"  {content_type}: {len(files)} file(s)")
    for file in files[:5]:  # Show first 5
        print(f"    - {file.name}")
```

Output example:
```
Model 0001 content:
  clips: 15 file(s)
    - clip001.mp4
    - clip002.mp4
    ...
  trailers: 1 file(s)
    - trailer.mp4
  previews: 8 file(s)
    - preview01.jpg
    - preview02.jpg
    ...
```

### 4. Comprehensive Model Information

Get detailed info about each model, similar to iStripper's model details:

```python
# Get complete model information
info = manager.get_model_info(models[0])

print(f"Model: {info['name']}")
print(f"Path: {info['path']}")
print(f"Total files: {info['total_files']}")
print(f"Total size: {info['total_size'] / 1024 / 1024:.1f} MB")
print(f"Subdirectories: {', '.join(info['subdirectories'])}")
print(f"Content types:")
for clip_type, files in info['clips'].items():
    print(f"  - {clip_type}: {len(files)} files")
```

### 5. Library-Wide Operations

Process your entire library like iStripper does:

```python
# Get info for ALL models
all_models_info = manager.get_all_models_info()

print(f"Total models: {len(all_models_info)}")

# Calculate library statistics
total_files = sum(m['total_files'] for m in all_models_info)
total_size_gb = sum(m['total_size'] for m in all_models_info) / 1024 / 1024 / 1024

print(f"Total files: {total_files}")
print(f"Total size: {total_size_gb:.2f} GB")

# Find largest models
largest = sorted(all_models_info, key=lambda m: m['total_size'], reverse=True)[:10]
print("\nLargest models:")
for model in largest:
    size_mb = model['total_size'] / 1024 / 1024
    print(f"  {model['name']}: {size_mb:.1f} MB")
```

### 6. Search and Filter Models

Find specific models just like searching in iStripper:

```python
# Search by name pattern
results = manager.search_models(pattern="0001")
print(f"Found {len(results)} models matching '0001'")

# Find models with clips
models_with_clips = manager.search_models(has_clips=True)
print(f"Found {len(models_with_clips)} models with clips")

# Find models within size range (10MB - 500MB)
size_filtered = manager.search_models(
    min_size=10 * 1024 * 1024,
    max_size=500 * 1024 * 1024
)
print(f"Found {len(size_filtered)} models between 10-500 MB")

# Combine filters
results = manager.search_models(
    pattern="girl",
    has_clips=True,
    min_size=50 * 1024 * 1024
)
```

## Advanced Usage Scenarios

### Scenario 1: Create Complete Model Playlist

Create a playlist that includes all clips from multiple models:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

manager = IStripperManager()
manager.detect_installation()

# Get all clips from first 10 models
all_clips_dict = manager.get_all_model_clips(limit=10)

# Build complete playlist
playlist = []
for model_name, clips_by_type in all_clips_dict.items():
    # Add main clips
    if 'clips' in clips_by_type:
        for clip in clips_by_type['clips']:
            playlist.append({
                'model': model_name,
                'type': 'clip',
                'path': str(clip),
                'filename': clip.name
            })
    
    # Add trailers
    if 'trailers' in clips_by_type:
        for trailer in clips_by_type['trailers']:
            playlist.append({
                'model': model_name,
                'type': 'trailer',
                'path': str(trailer),
                'filename': trailer.name
            })

print(f"Created playlist with {len(playlist)} items")
for item in playlist[:10]:
    print(f"  [{item['type']}] {item['model']}/{item['filename']}")
```

### Scenario 2: Model Rotation System

Rotate through all models automatically:

```python
import random
import time
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

class ModelRotator:
    def __init__(self):
        self.manager = IStripperManager()
        self.manager.detect_installation()
        self.all_clips = self.manager.get_all_model_clips()
        self.model_names = list(self.all_clips.keys())
        self.current_index = 0
    
    def get_next_model_clips(self):
        """Get clips from next model in sequence"""
        if not self.model_names:
            return None
        
        model_name = self.model_names[self.current_index]
        clips = self.all_clips[model_name]
        
        # Move to next model
        self.current_index = (self.current_index + 1) % len(self.model_names)
        
        return {
            'model': model_name,
            'clips': clips
        }
    
    def get_random_model_clips(self):
        """Get clips from random model"""
        if not self.model_names:
            return None
        
        model_name = random.choice(self.model_names)
        return {
            'model': model_name,
            'clips': self.all_clips[model_name]
        }

# Usage
rotator = ModelRotator()

# Sequential rotation
for _ in range(5):
    model_data = rotator.get_next_model_clips()
    if model_data:
        print(f"Now showing: {model_data['model']}")
        for clip_type, files in model_data['clips'].items():
            print(f"  {clip_type}: {len(files)} clips")
```

### Scenario 3: Content Type Selector

Select specific content types across all models:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

def get_all_content_by_type(content_type='clips', limit=None):
    """
    Get all content of a specific type across all models
    
    Args:
        content_type: 'clips', 'trailers', or 'previews'
        limit: Maximum number of models to process
    """
    manager = IStripperManager()
    manager.detect_installation()
    
    all_clips = manager.get_all_model_clips(limit=limit)
    
    result = []
    for model_name, clips_by_type in all_clips.items():
        if content_type in clips_by_type:
            for file in clips_by_type[content_type]:
                result.append({
                    'model': model_name,
                    'path': str(file),
                    'filename': file.name,
                    'size': file.stat().st_size
                })
    
    return result

# Get all main clips
all_clips = get_all_content_by_type('clips', limit=20)
print(f"Found {len(all_clips)} clips across models")

# Get all trailers
all_trailers = get_all_content_by_type('trailers', limit=20)
print(f"Found {len(all_trailers)} trailers across models")

# Get all previews
all_previews = get_all_content_by_type('previews', limit=20)
print(f"Found {len(all_previews)} previews across models")
```

### Scenario 4: Smart Library Browser

Create a smart browser that mimics iStripper's library interface:

```python
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

class LibraryBrowser:
    def __init__(self):
        self.manager = IStripperManager()
        self.manager.detect_installation()
        self.models_info = self.manager.get_all_models_info()
    
    def show_library_overview(self):
        """Display library overview like iStripper"""
        print("=" * 70)
        print("MODEL LIBRARY")
        print("=" * 70)
        print()
        
        total_models = len(self.models_info)
        total_files = sum(m['total_files'] for m in self.models_info)
        total_size = sum(m['total_size'] for m in self.models_info)
        models_with_clips = sum(1 for m in self.models_info if any(m['clips'].values()))
        
        print(f"Total Models:       {total_models}")
        print(f"Models with Clips:  {models_with_clips}")
        print(f"Total Files:        {total_files}")
        print(f"Library Size:       {total_size / 1024 / 1024 / 1024:.2f} GB")
        print()
    
    def list_models(self, page=1, per_page=20):
        """List models with pagination"""
        start = (page - 1) * per_page
        end = start + per_page
        page_models = self.models_info[start:end]
        
        print(f"Models (Page {page}):")
        print("-" * 70)
        
        for i, model in enumerate(page_models, start + 1):
            size_mb = model['total_size'] / 1024 / 1024
            clip_count = sum(len(clips) for clips in model['clips'].values())
            print(f"{i:3d}. {model['name']:<15} | {size_mb:6.1f} MB | {clip_count:3d} clips")
        
        total_pages = (len(self.models_info) + per_page - 1) // per_page
        print(f"\nPage {page} of {total_pages}")
    
    def show_model_details(self, model_name):
        """Show detailed info for a specific model"""
        model = next((m for m in self.models_info if m['name'] == model_name), None)
        
        if not model:
            print(f"Model {model_name} not found")
            return
        
        print("=" * 70)
        print(f"MODEL: {model['name']}")
        print("=" * 70)
        print()
        print(f"Path:        {model['path']}")
        print(f"Total Files: {model['total_files']}")
        print(f"Total Size:  {model['total_size'] / 1024 / 1024:.1f} MB")
        print()
        
        if model['subdirectories']:
            print(f"Subdirectories: {', '.join(model['subdirectories'])}")
            print()
        
        if model['clips']:
            print("Content:")
            for clip_type, files in model['clips'].items():
                print(f"  {clip_type.upper()}:")
                for file in files[:10]:  # Show first 10
                    print(f"    - {file.name}")
                if len(files) > 10:
                    print(f"    ... and {len(files) - 10} more")
        print()

# Usage
browser = LibraryBrowser()
browser.show_library_overview()
browser.list_models(page=1)
browser.show_model_details("0001")
```

### Scenario 5: Background Video Queue Manager

Manage a queue of videos for LCD display:

```python
import random
from collections import deque
from thermalright_lcd_control.integrations.istripper_manager import IStripperManager

class VideoQueueManager:
    def __init__(self, queue_size=10):
        self.manager = IStripperManager()
        self.manager.detect_installation()
        self.queue_size = queue_size
        self.queue = deque(maxlen=queue_size)
        self.history = []
        
        # Load initial queue
        self._fill_queue()
    
    def _fill_queue(self):
        """Fill queue with videos from different models"""
        all_clips = self.manager.get_all_model_clips()
        
        # Get videos from different models
        models = list(all_clips.keys())
        random.shuffle(models)
        
        for model_name in models:
            if len(self.queue) >= self.queue_size:
                break
            
            clips_by_type = all_clips[model_name]
            if 'clips' in clips_by_type and clips_by_type['clips']:
                video = random.choice(clips_by_type['clips'])
                self.queue.append({
                    'model': model_name,
                    'path': str(video),
                    'filename': video.name
                })
    
    def get_next_video(self):
        """Get next video from queue"""
        if not self.queue:
            self._fill_queue()
        
        if self.queue:
            video = self.queue.popleft()
            self.history.append(video)
            
            # Refill if queue is getting low
            if len(self.queue) < self.queue_size // 2:
                self._fill_queue()
            
            return video
        
        return None
    
    def skip_current_model(self):
        """Skip all videos from current model"""
        if not self.history:
            return
        
        current_model = self.history[-1]['model']
        self.queue = deque(
            [v for v in self.queue if v['model'] != current_model],
            maxlen=self.queue_size
        )
        self._fill_queue()
    
    def get_queue_status(self):
        """Get current queue status"""
        return {
            'queue_length': len(self.queue),
            'history_length': len(self.history),
            'models_in_queue': len(set(v['model'] for v in self.queue)),
            'current_model': self.history[-1]['model'] if self.history else None
        }

# Usage
queue_manager = VideoQueueManager(queue_size=20)

# Get next videos
for _ in range(5):
    video = queue_manager.get_next_video()
    if video:
        print(f"Now playing: {video['model']}/{video['filename']}")

# Check queue status
status = queue_manager.get_queue_status()
print(f"\nQueue: {status['queue_length']} videos, {status['models_in_queue']} models")
```

## API Reference - Full Interface Compatibility

### Core Methods

#### `list_model_directories()` -> List[Path]
Lists all model directories, exactly like iStripper's model library.

#### `get_model_media_files(model_dir, extensions=None, recursive=True)` -> List[Path]
Gets all media files from a model, with recursive subdirectory support.
- `recursive=True` - Default, searches all subdirectories (like iStripper)
- `recursive=False` - Only top-level files

#### `get_model_clips(model_dir)` -> Dict
Gets clips organized by type (clips/trailers/previews), matching iStripper's organization.

#### `get_model_info(model_dir)` -> Dict
Gets comprehensive model information:
- name, path, total_files, total_size, subdirectories, clips

#### `get_all_models_info(limit=None)` -> List[Dict]
Gets info for all models, like iStripper's library view.

#### `get_all_model_clips(limit=None)` -> Dict
Gets all clips from all models, organized by model and type.

#### `search_models(pattern, has_clips, min_size, max_size)` -> List[Dict]
Search and filter models by criteria.

### Model Info Dictionary Structure

```python
{
    'name': '0001',
    'path': 'C:/Program Files/iStripper/DATA/0001',
    'total_files': 25,
    'total_size': 524288000,  # bytes
    'subdirectories': ['clips', 'trailers', 'previews'],
    'clips': {
        'clips': [Path(...), Path(...)],
        'trailers': [Path(...)],
        'previews': [Path(...), Path(...)]
    }
}
```

## Performance Considerations

### For Large Libraries

When you have many models (50+), use these optimization strategies:

```python
# 1. Use limits to process in batches
batch_1 = manager.get_all_models_info(limit=50)
batch_2 = manager.get_all_models_info(limit=50)  # Note: this gets same 50

# Better: Process specific models
models = manager.list_model_directories()
for model in models[0:50]:
    info = manager.get_model_info(model)
    # Process info...

# 2. Cache results
all_info = manager.get_all_models_info()
# Store all_info and reuse instead of calling again

# 3. Use non-recursive search when you only need top-level files
files = manager.get_model_media_files(model, recursive=False)

# 4. Filter early with search
# Instead of loading all, then filtering
results = manager.search_models(has_clips=True, min_size=50*1024*1024)
```

## Troubleshooting

### Issue: Subdirectories Not Being Found

```python
# Check if model has subdirectories
model = models[0]
info = manager.get_model_info(model)
print(f"Subdirectories: {info['subdirectories']}")

# If empty but you know there are subdirectories, check manually
for item in model.iterdir():
    print(f"{item.name} - is_dir: {item.is_dir()}")
```

### Issue: Clips Dictionary Empty

```python
# Check the actual folder structure
clips = manager.get_model_clips(model)
if not clips:
    # Try getting all files regardless of subdirectory
    all_files = manager.get_model_media_files(model, recursive=True)
    print(f"Found {len(all_files)} files total")
    
    # Check what subdirectories exist
    for file in all_files[:10]:
        print(f"  {file.relative_to(model)}")
```

## Summary

This enhanced integration provides:

✅ **Complete library access** - All models, all subdirectories  
✅ **iStripper-like organization** - Clips/trailers/previews structure  
✅ **Comprehensive model info** - Size, counts, content types  
✅ **Search and filter** - Find specific models quickly  
✅ **Library statistics** - Overall metrics and analytics  
✅ **Recursive traversal** - No content left behind  
✅ **Production-ready** - Robust error handling and caching  

You can now build applications that work with your iStripper library just as comprehensively as iStripper itself does!
