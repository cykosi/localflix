"""
Routes for video streaming and related functionalities.
"""
import os
import re
from pathlib import Path
from flask import Blueprint, send_file, abort, current_app, request, Response

stream_bp = Blueprint('stream', __name__, url_prefix='/stream')

def get_range_header(range_header, file_size):
    """Parse the Range header and return start and end positions."""
    m = re.match(r'bytes=(?P<start>\d+)-(?P<end>\d*)', range_header)
    if not m:
        return 0, file_size - 1
    
    start = int(m.group('start'))
    end = m.group('end')
    end = int(end) if end else file_size - 1
    
    return start, min(end, file_size - 1)

@stream_bp.route('/<string:video_id>', methods=['GET'])
def stream_video(video_id):
    """
    Stream a video file with support for range requests (partial content).
    This enables seeking in the video player.
    """
    from utils.file_scanner import get_video_list
    
    video_dir = current_app.config['VIDEO_DIRECTORY']
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    
    # Get the video list and find the one with matching ID
    videos = get_video_list(video_dir, allowed_extensions)
    video_info = None
    
    for video in videos:
        if video['id'] == video_id:
            video_info = video
            break
    
    if not video_info:
        current_app.logger.error(f"Video not found in catalog for ID: {video_id}")
        abort(404)
    
    # Construct the full path using the video's path from the metadata
    video_path = os.path.join(video_dir, video_info['path'])
    
    if not os.path.isfile(video_path):
        current_app.logger.error(f"Video file not found at path: {video_path}")
        abort(404)
    
    file_size = os.path.getsize(video_path)
    range_header = request.headers.get('Range')
    
    # Handle range requests for video seeking
    if range_header:
        start, end = get_range_header(range_header, file_size)
        
        # Calculate the content length
        content_length = end - start + 1
        
        # Create a partial response
        def generate():
            with open(video_path, 'rb') as video_file:
                video_file.seek(start)
                data = video_file.read(min(content_length, 1024 * 1024))  # Read 1MB at a time
                while data:
                    yield data
                    content_length -= len(data)
                    if content_length <= 0:
                        break
                    data = video_file.read(min(content_length, 1024 * 1024))
        
        response = Response(generate(), 206, mimetype=f'video/{Path(video_path).suffix[1:]}',
                          content_type=f'video/{Path(video_path).suffix[1:]}')
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(content_length))
        return response
    
    # Return the full file if no range header
    return send_file(video_path)

@stream_bp.route('/thumbnail/<string:video_id>', methods=['GET'])
def get_thumbnail(video_id):
    """Get a thumbnail for a video."""
    thumbnail_dir = current_app.config['THUMBNAIL_DIRECTORY']
    
    # Look for existing thumbnail
    thumbnail_path = os.path.join(thumbnail_dir, f"{video_id}.jpg")
    
    if os.path.isfile(thumbnail_path):
        return send_file(thumbnail_path)
    else:
        # Try to generate a thumbnail on-demand if ffmpeg is available
        try:
            from utils.file_scanner import get_video_details
            from utils.video_helper import generate_thumbnail, check_dependencies
            
            video_dir = current_app.config['VIDEO_DIRECTORY']
            allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
            
            # Only attempt to generate if config allows it
            if current_app.config.get('GENERATE_THUMBNAILS', True) and check_dependencies():
                # Get video details to find the path
                video = get_video_details(video_id, video_dir, allowed_extensions)
                
                if video:
                    # Construct the full path to the video
                    video_path = os.path.join(video_dir, video['path'])
                    
                    # Try to generate the thumbnail
                    if generate_thumbnail(
                        video_path, 
                        thumbnail_path, 
                        time_offset=10, 
                        width=current_app.config.get('THUMBNAIL_WIDTH', 320)
                    ):
                        return send_file(thumbnail_path)
        except Exception as e:
            current_app.logger.error(f"Error generating thumbnail: {str(e)}")
        
        # Return a default thumbnail if no specific one exists or generation failed
        default_thumbnail = os.path.join(current_app.root_path, 'static', 'default-thumbnail.jpg')
        if os.path.isfile(default_thumbnail):
            return send_file(default_thumbnail)
        
        # If no default thumbnail, return 404
        abort(404)
