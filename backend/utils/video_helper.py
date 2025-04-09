"""
Utilities for video metadata extraction and thumbnail generation.

Note: This module requires additional dependencies:
- ffmpeg-python for video processing
- Pillow for image manipulation
"""
import os
import tempfile
import subprocess
from pathlib import Path
from flask import current_app

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

def check_dependencies():
    """Check if the required dependencies are installed."""
    if not FFMPEG_AVAILABLE:
        current_app.logger.warning("ffmpeg-python is not installed. Video metadata and thumbnails will be limited.")
    
    if not PILLOW_AVAILABLE:
        current_app.logger.warning("Pillow is not installed. Thumbnail processing will be limited.")
    
    # Check if ffmpeg is installed on the system
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        current_app.logger.warning("ffmpeg command not found. Thumbnail generation will not work.")
        return False
    
    return FFMPEG_AVAILABLE and PILLOW_AVAILABLE

def get_video_metadata(video_path):
    """
    Extract metadata from a video file using ffmpeg.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        dict: Dictionary containing video metadata or empty dict if extraction failed
    """
    if not FFMPEG_AVAILABLE or not os.path.isfile(video_path):
        return {}
    
    try:
        # Use ffmpeg to get video metadata
        probe = ffmpeg.probe(video_path)
        
        # Extract relevant information
        metadata = {}
        
        # Get video stream info
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
        if video_streams:
            video_stream = video_streams[0]  # Use the first video stream
            metadata['width'] = video_stream.get('width')
            metadata['height'] = video_stream.get('height')
            metadata['codec'] = video_stream.get('codec_name')
            
            # Calculate aspect ratio
            if metadata.get('width') and metadata.get('height'):
                metadata['aspect_ratio'] = f"{metadata['width']}:{metadata['height']}"
            
            # Get duration if available
            if 'duration' in video_stream:
                duration_seconds = float(video_stream['duration'])
                metadata['duration'] = format_duration(duration_seconds)
                metadata['duration_seconds'] = duration_seconds
        
        # Get audio stream info
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
        if audio_streams:
            metadata['audio_codec'] = audio_streams[0].get('codec_name')
            metadata['audio_channels'] = audio_streams[0].get('channels')
        
        # Get format info
        if 'format' in probe:
            format_info = probe['format']
            metadata['format_name'] = format_info.get('format_name')
            metadata['size_bytes'] = int(format_info.get('size', 0))
            metadata['bit_rate'] = int(format_info.get('bit_rate', 0))
        
        return metadata
    
    except Exception as e:
        current_app.logger.error(f"Error extracting metadata from {video_path}: {str(e)}")
        return {}

def generate_thumbnail(video_path, output_path, time_offset=10, width=320):
    """
    Generate a thumbnail from a video file.
    
    Args:
        video_path (str): Path to the video file
        output_path (str): Path where the thumbnail should be saved
        time_offset (int): Time in seconds from the start of the video to capture the thumbnail
        width (int): Width of the thumbnail (height will be calculated to maintain aspect ratio)
        
    Returns:
        bool: True if thumbnail generation was successful, False otherwise
    """
    if not os.path.isfile(video_path):
        return False
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Temporary file for the extracted frame
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Use ffmpeg to extract a frame from the video
        subprocess.run([
            'ffmpeg',
            '-i', video_path,
            '-ss', str(time_offset),
            '-frames:v', '1',
            '-q:v', '2',
            temp_path
        ], check=True, capture_output=True)
        
        # Resize the thumbnail if Pillow is available
        if PILLOW_AVAILABLE:
            with Image.open(temp_path) as img:
                # Calculate height to maintain aspect ratio
                width_percent = width / float(img.size[0])
                height = int(float(img.size[1]) * width_percent)
                
                # Resize the image
                img_resized = img.resize((width, height), Image.LANCZOS)
                img_resized.save(output_path, 'JPEG', quality=90)
        else:
            # If Pillow is not available, just copy the extracted frame
            os.rename(temp_path, output_path)
        
        # Clean up the temporary file if it still exists
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return True
    
    except Exception as e:
        current_app.logger.error(f"Error generating thumbnail for {video_path}: {str(e)}")
        
        # Clean up any temporary files
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return False

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"
