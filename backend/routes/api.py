"""
API routes for video listings and metadata.
"""
from flask import Blueprint, jsonify, current_app, request
from utils.file_scanner import get_video_list, get_video_details

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/videos', methods=['GET'])
def get_videos():
    """
    Get a list of all available videos.
    
    Query parameters:
    - sort: Sort by 'name', 'date', 'size' (default: 'name')
    - order: 'asc' or 'desc' (default: 'asc')
    """
    sort_by = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    
    try:
        videos = get_video_list(
            video_dir=current_app.config['VIDEO_DIRECTORY'],
            allowed_extensions=current_app.config['ALLOWED_EXTENSIONS'],
            sort_by=sort_by,
            order=order
        )
        return jsonify({'videos': videos, 'count': len(videos)})
    except Exception as e:
        current_app.logger.error(f"Error getting video list: {str(e)}")
        return jsonify({'error': 'Failed to get video list'}), 500

@api_bp.route('/videos/<string:video_id>', methods=['GET'])
def get_video(video_id):
    """Get details for a specific video by ID."""
    try:
        video = get_video_details(
            video_id=video_id,
            video_dir=current_app.config['VIDEO_DIRECTORY'],
            allowed_extensions=current_app.config['ALLOWED_EXTENSIONS']
        )
        
        if video:
            return jsonify(video)
        else:
            return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Error getting video details: {str(e)}")
        return jsonify({'error': 'Failed to get video details'}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about the video library."""
    try:
        videos = get_video_list(
            video_dir=current_app.config['VIDEO_DIRECTORY'],
            allowed_extensions=current_app.config['ALLOWED_EXTENSIONS']
        )
        
        # Calculate basic stats
        total_videos = len(videos)
        formats = {}
        for video in videos:
            ext = video.get('format', 'unknown')
            formats[ext] = formats.get(ext, 0) + 1
        
        # You can add more stats here as needed
        
        return jsonify({
            'total_videos': total_videos,
            'formats': formats
        })
    except Exception as e:
        current_app.logger.error(f"Error getting library stats: {str(e)}")
        return jsonify({'error': 'Failed to get library statistics'}), 500
