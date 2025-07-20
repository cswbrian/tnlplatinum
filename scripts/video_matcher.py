#!/usr/bin/env python3
"""
Main Video Matcher Script
Orchestrates the entire video matching and JSON updating process
"""

import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

from playlist_extractor import PlaylistExtractor
from matching_algorithm import TitleMatcher
from json_updater import JSONUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'video_matcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class VideoMatcher:
    def __init__(self, min_confidence: float = 75.0):
        self.extractor = PlaylistExtractor()
        self.matcher = TitleMatcher(min_confidence=min_confidence)
        self.updater = JSONUpdater()
        
        # Define which playlists map to which JSON files
        self.playlist_to_json_mapping = {
            '試映劇場': ['films'],  # Films only, not ads
            '試音片': ['audition-films'],  # Audition films, not songs
            '試乜都得': ['variety-shows'],
            '試玩毛': ['variety-shows'],
            '口試王': ['variety-shows'],
            '學術研討會': ['variety-shows'],
            '誠實測慌機': ['variety-shows'],
            '同囚易': ['variety-shows'],
            '忍笑': ['variety-shows'],
            'channel_videos': ['variety-shows', 'films', 'songs', 'ads', 'audition-films'],  # Channel videos can match any type
        }
        
        # Files that contain video content (exclude supporting-actors.json which is just strings)
        self.video_content_files = ['variety-shows', 'films', 'songs', 'ads', 'audition-films']

    def extract_all_videos(self, include_channel_videos: bool = False, channel_url: str = None) -> Dict[str, List[Dict]]:
        """Extract videos from all playlists and optionally channel videos"""
        if include_channel_videos and channel_url:
            logger.info("Starting video extraction from YouTube playlists and channel videos...")
            all_videos = self.extractor.extract_all_videos_including_channel(channel_url)
        else:
            logger.info("Starting video extraction from YouTube playlists...")
            all_videos = self.extractor.extract_all_playlists()
        
        total_videos = sum(len(videos) for videos in all_videos.values())
        logger.info(f"Extracted {total_videos} total videos from {len(all_videos)} sources")
        
        return all_videos

    def process_playlist_for_json_file(self, playlist_name: str, videos: List[Dict], json_file_type: str) -> List[Dict]:
        """Process videos from a specific playlist for a specific JSON file"""
        logger.info(f"Processing {len(videos)} videos from '{playlist_name}' for {json_file_type}.json")
        
        # Load JSON data
        json_data = self.updater.load_json_file(self.updater.json_files[json_file_type])
        if not json_data:
            logger.warning(f"No data loaded for {json_file_type}.json")
            return []
        
        # Find matches
        matches = self.matcher.match_videos_to_json(videos, json_data)
        
        logger.info(f"Found {len(matches)} matches for {json_file_type}.json")
        return matches

    def run_matching_process(self, include_channel_videos: bool = False, channel_url: str = None) -> Dict[str, Any]:
        """Run the complete matching process"""
        logger.info("Starting video matching process...")
        
        # Extract all videos
        all_videos = self.extract_all_videos(include_channel_videos, channel_url)
        
        # Process each playlist-to-JSON mapping
        all_matches = {}
        total_matches = 0
        
        for playlist_name, json_file_types in self.playlist_to_json_mapping.items():
            if playlist_name not in all_videos:
                logger.warning(f"Playlist '{playlist_name}' not found in extracted videos")
                continue
            
            playlist_videos = all_videos[playlist_name]
            
            for json_file_type in json_file_types:
                logger.info(f"\n--- Processing {playlist_name} → {json_file_type}.json ---")
                
                matches = self.process_playlist_for_json_file(playlist_name, playlist_videos, json_file_type)
                
                if matches:
                    if json_file_type not in all_matches:
                        all_matches[json_file_type] = []
                    all_matches[json_file_type].extend(matches)
                    total_matches += len(matches)
        
        logger.info(f"\nTotal matches found: {total_matches}")
        return all_matches

    def apply_matches(self, all_matches: Dict[str, List[Dict]], dry_run: bool = False) -> Dict[str, int]:
        """Apply matches to JSON files"""
        if dry_run:
            logger.info("DRY RUN MODE - No files will be modified")
        
        update_results = {}
        
        for json_file_type, matches in all_matches.items():
            logger.info(f"\n--- Updating {json_file_type}.json with {len(matches)} matches ---")
            
            if dry_run:
                # Just report what would be updated
                update_results[json_file_type] = len(matches)
                for match in matches:
                    entry_id = match['json_entry'].get('id', 'N/A')
                    title = match['json_entry'].get('title', 'Unknown')
                    confidence = match['confidence']
                    logger.info(f"  Would update ID {entry_id}: '{title}' (confidence: {confidence:.1f})")
            else:
                # Actually update the file
                updates_made = self.updater.apply_matches_to_file(json_file_type, matches)
                update_results[json_file_type] = updates_made
        
        return update_results

    def generate_report(self, all_matches: Dict[str, List[Dict]], update_results: Dict[str, int]) -> Dict:
        """Generate comprehensive report"""
        # Get file statistics only for video content files
        file_stats = {}
        for file_type in self.video_content_files:
            file_stats[file_type] = self.updater.get_file_statistics(file_type)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_playlists_processed': len(self.playlist_to_json_mapping),
                'total_json_files_updated': len(update_results),
                'total_matches_found': sum(len(matches) for matches in all_matches.values()),
                'total_updates_applied': sum(update_results.values())
            },
            'file_statistics': file_stats,
            'matches_by_file': {},
            'update_results': update_results
        }
        
        # Add detailed match information
        for json_file_type, matches in all_matches.items():
            report['matches_by_file'][json_file_type] = {
                'total_matches': len(matches),
                'high_confidence_matches': len([m for m in matches if m['confidence'] >= 90]),
                'medium_confidence_matches': len([m for m in matches if 75 <= m['confidence'] < 90]),
                'low_confidence_matches': len([m for m in matches if m['confidence'] < 75]),
                'matches': [
                    {
                        'video_title': m['video']['title'],
                        'json_title': m['json_entry'].get('title', ''),
                        'confidence': m['confidence'],
                        'video_url': m['video_url'],
                        'playlist': m['video']['playlist']
                    }
                    for m in matches
                ]
            }
        
        return report

    def save_report(self, report: Dict, filename: str = None) -> str:
        """Save report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_matching_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"Report saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            return ""

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Match YouTube videos to JSON data files')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying them')
    parser.add_argument('--min-confidence', type=float, default=75.0, help='Minimum match confidence (0-100)')
    parser.add_argument('--report-only', action='store_true', help='Generate report without updating files')
    parser.add_argument('--include-channel', action='store_true', help='Include main channel videos in addition to playlists')
    parser.add_argument('--channel-url', type=str, default='https://www.youtube.com/@trialanderror924/videos', help='Channel videos URL')
    
    args = parser.parse_args()
    
    # Initialize matcher
    matcher = VideoMatcher(min_confidence=args.min_confidence)
    
    # Run matching process
    all_matches = matcher.run_matching_process(
        include_channel_videos=args.include_channel,
        channel_url=args.channel_url if args.include_channel else None
    )
    
    # Apply matches (or dry run)
    if not args.report_only:
        update_results = matcher.apply_matches(all_matches, dry_run=args.dry_run)
    else:
        update_results = {k: len(v) for k, v in all_matches.items()}
    
    # Generate and save report
    report = matcher.generate_report(all_matches, update_results)
    report_file = matcher.save_report(report)
    
    # Print summary
    print(f"\n{'='*60}")
    print("VIDEO MATCHING SUMMARY")
    print(f"{'='*60}")
    print(f"Total matches found: {report['summary']['total_matches_found']}")
    print(f"Total updates applied: {report['summary']['total_updates_applied']}")
    print(f"Report saved to: {report_file}")
    
    print(f"\nMatches by file:")
    for file_type, file_matches in report['matches_by_file'].items():
        print(f"  {file_type}.json: {file_matches['total_matches']} matches "
              f"({file_matches['high_confidence_matches']} high confidence)")
    
    print(f"\nCurrent coverage:")
    for file_type, stats in report['file_statistics'].items():
        print(f"  {file_type}.json: {stats['entries_with_urls']}/{stats['total_entries']} "
              f"({stats['url_coverage']:.1f}%) have video URLs")
    
    if args.dry_run:
        print(f"\nDRY RUN MODE - No files were modified")
        print(f"Run without --dry-run to apply changes")

if __name__ == "__main__":
    main()