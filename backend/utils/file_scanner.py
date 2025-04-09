"""
Utilities for scanning the filesystem for video files.
"""
import os
import time
import hashlib
from datetime import datetime
from pathlib import Path

# Cache for video listings to avoid excessive file system operations
_video_cache = {
    'last_scan': 0,
    'videos': []
}

def should_rescan(scan_interval):
    """Determine if a rescan is needed based on the last scan time."""
    current_time = time.time()
    return current_time - _video_cache['last_scan'] > scan_interval

def generate_video_id(file_path):
    """Generate a unique ID for a video file based on its path."""
    # We use a hash of the file path to create a unique, URL-friendly ID
    return hashlib.md5(file_path.encode('utf-8')).hexdigest()

def get_video_list(video_dir, allowed_extensions, sort_by='name', order='asc', force_rescan=False, scan_interval=3600):
    """
    Get a list of all video files in the specified directory.
    
    Args:
        video_dir (str): The directory to scan for videos
        allowed_extensions (set): Set of allowed file extensions
        sort_by (str): Field to sort by ('name', 'date', 'size')
        order (str): Sort order ('asc' or 'desc')
        force_rescan (bool): Force a rescan even if cache is valid
        scan_interval (int): Time in seconds before rescanning
        
    Returns:
        list: List of dictionaries with video information
    """
    # Check if we need to rescan
    if force_rescan or should_rescan(scan_interval) or not _video_cache['videos']:
        videos = []
        
        # Walk through all files in the video directory
        for root, _, files in os.walk(video_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1][1:].lower()
                
                if file_ext in allowed_extensions:
                    # Get file stats
                    stats = os.stat(file_path)
                    
                    # Extract information
                    video_id = generate_video_id(file_path)
                    rel_path = os.path.relpath(file_path, video_dir)
                    
                    video_info = {
                        'id': video_id,
                        'name': os.path.splitext(os.path.basename(file))[0],
                        'path': rel_path,
                        'format': file_ext,
                        'size': stats.st_size,
                        'size_human': format_file_size(stats.st_size),
                        'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stats.st_ctime).isoformat()
                    }
                    
                    videos.append(video_info)
        
        # Update cache
        _video_cache['videos'] = videos
        _video_cache['last_scan'] = time.time()
    
    # Get videos from cache and apply sorting
    result = _video_cache['videos'].copy()
    
    # Apply sorting
    if sort_by == 'name':
        result.sort(key=lambda x: x['name'].lower(), reverse=(order.lower() == 'desc'))
    elif sort_by == 'date':
        result.sort(key=lambda x: x['modified'], reverse=(order.lower() == 'desc'))
    elif sort_by == 'size':
        result.sort(key=lambda x: x['size'], reverse=(order.lower() == 'desc'))
    
    return result

def get_video_details(video_id, video_dir, allowed_extensions):
    """
    Get detailed information about a specific video.
    
    Args:
        video_id (str): The ID of the video to retrieve
        video_dir (str): The base directory for videos
        allowed_extensions (set): Set of allowed file extensions
        
    Returns:
        dict: Dictionary with video details or None if not found
    """
    videos = get_video_list(video_dir, allowed_extensions)
    
    # Find the video with the matching ID
    for video in videos:
        if video['id'] == video_id:
            # Here you could add additional details like video duration, resolution, etc.
            # This would require using a library like ffmpeg-python or pymediainfo
            return video
    
    return None

def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0 or unit == 'TB':
            break
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} {unit}"
