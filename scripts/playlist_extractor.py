#!/usr/bin/env python3
"""
YouTube Playlist Video Extractor
Extracts video information from Trial and Error YouTube playlists
"""

import yt_dlp
import json
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlaylistExtractor:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'no_warnings': True,
        }
        
        # Define playlists to extract from
        self.playlists = {
            '試乜都得': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aozuqn3o19RKIVd6RGn-_zPI',
            '試玩毛': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aox5LUrnyVSfdaPBSLbBzp9K',
            '試映劇場': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aoyk4uZzloDcD33ASnyW6Opr',
            '試音片': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aoxBmc7YOdanbS0WDiAldtUJ',
            '口試王': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aozWogb4Idc2uridkwqkS137',
            '學術研討會': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aozYYp-COZA8CuOqRPagvfQU',
            '誠實測慌機': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aoy_9SLs15JJ0QrZIZlja6Ar',
            '同囚易': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aozRXTb_W5UXc0npNHHoa69a',
            '忍笑': 'https://www.youtube.com/playlist?list=PL1HEsuKH_aoxdrdojn5q_3_Y0hINcx_cf',
        }

    def extract_playlist_videos(self, playlist_url: str, playlist_name: str) -> List[Dict]:
        """Extract videos from a single playlist"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                logger.info(f"Extracting playlist: {playlist_name}")
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                videos = []
                if 'entries' in playlist_info:
                    for entry in playlist_info['entries']:
                        if entry and 'title' in entry and 'url' in entry:
                            video = {
                                'title': entry['title'],
                                'url': entry['url'],
                                'playlist': playlist_name,
                                'id': entry.get('id', ''),
                                'duration': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0)
                            }
                            videos.append(video)
                
                logger.info(f"Extracted {len(videos)} videos from {playlist_name}")
                return videos
                
        except Exception as e:
            logger.error(f"Error extracting playlist {playlist_name}: {str(e)}")
            return []

    def extract_channel_videos(self, channel_url: str, limit: int = 500) -> List[Dict]:
        """Extract videos from main channel videos page"""
        try:
            # Configure yt-dlp for channel video extraction
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'no_warnings': True,
                'playlistend': limit,  # Limit number of videos to extract
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Extracting videos from channel: {channel_url}")
                channel_info = ydl.extract_info(channel_url, download=False)
                
                videos = []
                if 'entries' in channel_info:
                    for entry in channel_info['entries']:
                        if entry and 'title' in entry and 'url' in entry:
                            video = {
                                'title': entry['title'],
                                'url': entry['url'],
                                'playlist': 'channel_videos',
                                'id': entry.get('id', ''),
                                'duration': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                                'upload_date': entry.get('upload_date', '')
                            }
                            videos.append(video)
                
                logger.info(f"Extracted {len(videos)} videos from channel")
                return videos
                
        except Exception as e:
            logger.error(f"Error extracting channel videos: {str(e)}")
            return []

    def extract_all_playlists(self) -> Dict[str, List[Dict]]:
        """Extract videos from all playlists"""
        all_videos = {}
        
        for playlist_name, playlist_url in self.playlists.items():
            videos = self.extract_playlist_videos(playlist_url, playlist_name)
            all_videos[playlist_name] = videos
            
        return all_videos

    def extract_all_videos_including_channel(self, channel_url: str = None) -> Dict[str, List[Dict]]:
        """Extract videos from all playlists plus main channel videos"""
        all_videos = self.extract_all_playlists()
        
        if channel_url:
            channel_videos = self.extract_channel_videos(channel_url)
            all_videos['channel_videos'] = channel_videos
            
        return all_videos

    def save_to_json(self, data: Dict, filename: str = 'extracted_videos.json'):
        """Save extracted video data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

    def get_all_videos_flat(self) -> List[Dict]:
        """Get all videos in a flat list with playlist source"""
        all_data = self.extract_all_playlists()
        flat_videos = []
        
        for playlist_name, videos in all_data.items():
            flat_videos.extend(videos)
            
        return flat_videos

if __name__ == "__main__":
    extractor = PlaylistExtractor()
    
    # Extract all videos
    all_videos = extractor.extract_all_playlists()
    
    # Save to JSON
    extractor.save_to_json(all_videos, 'extracted_videos.json')
    
    # Print summary
    total_videos = sum(len(videos) for videos in all_videos.values())
    print(f"\nExtraction Summary:")
    print(f"Total videos extracted: {total_videos}")
    
    for playlist_name, videos in all_videos.items():
        print(f"  {playlist_name}: {len(videos)} videos")