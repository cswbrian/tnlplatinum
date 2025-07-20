#!/usr/bin/env python3
"""
JSON File Updater
Updates JSON data files with matched video URLs while preserving structure
"""

import json
import os
import shutil
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class JSONUpdater:
    def __init__(self, data_dir: str = "../src/data"):
        self.data_dir = data_dir
        self.backup_dir = os.path.join(data_dir, "backups")
        self.ensure_backup_dir()
        
        # Define JSON files to update
        self.json_files = {
            'variety-shows': 'variety-shows.json',
            'films': 'films.json', 
            'songs': 'songs.json',
            'ads': 'ads.json',
            'audition-films': 'audition-films.json',
            'supporting-actors': 'supporting-actors.json'
        }

    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def backup_file(self, filename: str) -> str:
        """Create backup of JSON file before modification"""
        source_path = os.path.join(self.data_dir, filename)
        if not os.path.exists(source_path):
            logger.warning(f"File not found: {source_path}")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename}_{timestamp}.backup"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            shutil.copy2(source_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return ""

    def load_json_file(self, filename: str) -> List[Dict]:
        """Load JSON file data"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} entries from {filename}")
            return data
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            return []

    def save_json_file(self, filename: str, data: List[Dict]) -> bool:
        """Save JSON file with proper formatting"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(data)} entries to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {str(e)}")
            return False

    def update_entry_with_video_url(self, entry: Dict, video_url: str, confidence: float) -> Dict:
        """Update a single entry with video URL"""
        updated_entry = entry.copy()
        
        # Add videoUrl field
        updated_entry['videoUrl'] = video_url
        
        # Add metadata about the match (optional)
        # updated_entry['_match_confidence'] = confidence
        # updated_entry['_match_timestamp'] = datetime.now().isoformat()
        
        return updated_entry

    def apply_matches_to_file(self, file_type: str, matches: List[Dict]) -> int:
        """Apply video URL matches to a specific JSON file"""
        if file_type not in self.json_files:
            logger.error(f"Unknown file type: {file_type}")
            return 0
        
        filename = self.json_files[file_type]
        
        # Create backup
        backup_path = self.backup_file(filename)
        if not backup_path:
            logger.error(f"Cannot proceed without backup for {filename}")
            return 0
        
        # Load current data
        data = self.load_json_file(filename)
        if not data:
            return 0
        
        # Apply matches
        updates_made = 0
        for match in matches:
            json_entry = match['json_entry']
            video_url = match['video_url']
            confidence = match['confidence']
            
            # Find the entry in the data by ID or other unique identifier
            entry_id = json_entry.get('id')
            if entry_id is not None:
                for i, entry in enumerate(data):
                    if entry.get('id') == entry_id:
                        # Only update if no videoUrl exists, if this is a better match, or if URL is different
                        existing_url = entry.get('videoUrl')
                        if not existing_url or confidence > 95 or existing_url != video_url:
                            if existing_url and existing_url != video_url:
                                logger.info(f"Replacing existing URL for ID {entry_id}: {existing_url} -> {video_url}")
                            data[i] = self.update_entry_with_video_url(entry, video_url, confidence)
                            updates_made += 1
                            logger.info(f"Updated entry ID {entry_id} with video URL (confidence: {confidence:.1f})")
                        else:
                            logger.debug(f"Skipping duplicate update for ID {entry_id} (existing URL: {existing_url})")
                        break
            else:
                # For files without ID, match by title
                title = json_entry.get('title', '')
                for i, entry in enumerate(data):
                    if entry.get('title') == title:
                        if not entry.get('videoUrl') or confidence > 95:
                            data[i] = self.update_entry_with_video_url(entry, video_url, confidence)
                            updates_made += 1
                            logger.info(f"Updated entry '{title}' with video URL (confidence: {confidence:.1f})")
                        break
        
        # Save updated data
        if updates_made > 0:
            if self.save_json_file(filename, data):
                logger.info(f"Applied {updates_made} updates to {filename}")
            else:
                logger.error(f"Failed to save updates to {filename}")
                return 0
        else:
            logger.info(f"No updates needed for {filename}")
        
        return updates_made

    def get_file_statistics(self, file_type: str) -> Dict:
        """Get statistics about a JSON file"""
        if file_type not in self.json_files:
            return {}
        
        filename = self.json_files[file_type]
        data = self.load_json_file(filename)
        
        total_entries = len(data)
        
        # Handle different data structures - some files contain strings, others contain objects
        if data and isinstance(data[0], dict):
            entries_with_urls = sum(1 for entry in data if isinstance(entry, dict) and entry.get('videoUrl'))
        else:
            # For files with string arrays (like supporting-actors.json), no video URLs are expected
            entries_with_urls = 0
        
        entries_without_urls = total_entries - entries_with_urls
        
        return {
            'filename': filename,
            'total_entries': total_entries,
            'entries_with_urls': entries_with_urls,
            'entries_without_urls': entries_without_urls,
            'url_coverage': (entries_with_urls / total_entries * 100) if total_entries > 0 else 0
        }

    def generate_update_report(self) -> Dict:
        """Generate comprehensive report of all JSON files"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'files': {}
        }
        
        for file_type in self.json_files.keys():
            report['files'][file_type] = self.get_file_statistics(file_type)
        
        return report

    def validate_video_urls(self, file_type: str) -> List[Dict]:
        """Validate that video URLs in file are accessible"""
        if file_type not in self.json_files:
            return []
        
        filename = self.json_files[file_type]
        data = self.load_json_file(filename)
        
        issues = []
        for entry in data:
            video_url = entry.get('videoUrl')
            if video_url:
                # Basic URL validation
                if not video_url.startswith('https://www.youtube.com/watch?v='):
                    issues.append({
                        'entry_id': entry.get('id'),
                        'title': entry.get('title'),
                        'issue': 'Invalid URL format',
                        'url': video_url
                    })
        
        return issues

if __name__ == "__main__":
    # Test the updater
    updater = JSONUpdater()
    
    # Generate report of current state
    report = updater.generate_update_report()
    print("Current JSON file statistics:")
    for file_type, stats in report['files'].items():
        print(f"  {file_type}: {stats['entries_with_urls']}/{stats['total_entries']} "
              f"({stats['url_coverage']:.1f}%) have video URLs")