#!/usr/bin/env python3
"""
Smart Title Matching Algorithm
Matches YouTube video titles to JSON data entries using various strategies
"""

import re
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz, process
import logging

logger = logging.getLogger(__name__)

class TitleMatcher:
    def __init__(self, min_confidence: float = 70.0):
        self.min_confidence = min_confidence
        
        # Define playlist to data file mappings
        self.playlist_mappings = {
            '試映劇場': ['films', 'ads'],  # Films and sponsored content
            '試音片': ['songs'],           # Music videos
            '試乜都得': ['variety-shows'], # Variety shows
            '試玩毛': ['variety-shows'],   # Game shows
            '口試王': ['variety-shows'],   # Debate shows
            '學術研討會': ['variety-shows'], # Academic discussions
            '誠實測慌機': ['variety-shows'], # Truth detector shows
            '同囚易': ['variety-shows'],   # Reality shows
            '忍笑': ['variety-shows'],     # Comedy shows
        }

    def clean_title(self, title: str) -> str:
        """Clean title for better matching"""
        if not title:
            return ""
        
        # Remove common suffixes and prefixes
        title = re.sub(r'\s*[｜|]\s*試當真.*$', '', title)
        title = re.sub(r'\s*-\s*YouTube.*$', '', title)
        title = re.sub(r'^\s*試映劇場\s*[《〈]?', '', title)
        title = re.sub(r'^\s*試音片\s*[《〈]?', '', title)
        title = re.sub(r'^\s*試乜都得\s*[《〈]?', '', title)
        title = re.sub(r'[》〉]\s*$', '', title)
        
        # Normalize whitespace
        title = re.sub(r'\s+', ' ', title)
        return title.strip()

    def extract_episode_info(self, title: str) -> Tuple[str, Optional[str]]:
        """Extract episode number/series info"""
        # Look for episode patterns like EP01, EP1, etc.
        ep_match = re.search(r'EP(\d+)', title, re.IGNORECASE)
        if ep_match:
            episode = ep_match.group(0)
            base_title = title.replace(episode, '').strip()
            return base_title, episode
        
        return title, None

    def calculate_match_score(self, video_title: str, json_title: str, json_full_title: str = "") -> float:
        """Calculate comprehensive match score between video and JSON titles"""
        
        # Clean titles for comparison
        clean_video = self.clean_title(video_title)
        clean_json = self.clean_title(json_title)
        clean_full = self.clean_title(json_full_title)
        
        scores = []
        
        # 1. Exact match (highest score)
        if clean_video == clean_json or clean_video == clean_full:
            return 100.0
        
        # 2. Substring matches
        if clean_json in clean_video or clean_video in clean_json:
            scores.append(95.0)
        if clean_full and (clean_full in clean_video or clean_video in clean_full):
            scores.append(95.0)
        
        # 3. Fuzzy string matching
        scores.append(fuzz.ratio(clean_video, clean_json))
        if clean_full:
            scores.append(fuzz.ratio(clean_video, clean_full))
        
        # 4. Token-based matching (good for reordered words)
        scores.append(fuzz.token_sort_ratio(clean_video, clean_json))
        if clean_full:
            scores.append(fuzz.token_sort_ratio(clean_video, clean_full))
        
        # 5. Partial ratio (for substring similarity)
        scores.append(fuzz.partial_ratio(clean_video, clean_json))
        if clean_full:
            scores.append(fuzz.partial_ratio(clean_video, clean_full))
        
        # 6. Episode-specific matching
        video_base, video_ep = self.extract_episode_info(clean_video)
        json_base, json_ep = self.extract_episode_info(clean_json)
        
        if video_ep and json_ep and video_ep == json_ep:
            # Same episode number, boost score
            base_score = fuzz.ratio(video_base, json_base)
            scores.append(min(base_score + 20, 100))
        
        return max(scores) if scores else 0.0

    def find_best_match(self, video: Dict, json_entries: List[Dict]) -> Tuple[Optional[Dict], float]:
        """Find the best matching JSON entry for a video"""
        video_title = video.get('title', '')
        playlist = video.get('playlist', '')
        
        best_match = None
        best_score = 0.0
        
        for entry in json_entries:
            title = entry.get('title', '')
            full_title = entry.get('fullTitle', '')
            
            # Skip if entry already has a videoUrl (unless we're verifying)
            if entry.get('videoUrl') and video.get('url') != entry.get('videoUrl'):
                continue
            
            score = self.calculate_match_score(video_title, title, full_title)
            
            # Boost score for playlist-appropriate matches
            if self.is_playlist_appropriate(playlist, entry):
                score += 5.0
            
            if score > best_score and score >= self.min_confidence:
                best_score = score
                best_match = entry
        
        return best_match, best_score

    def is_playlist_appropriate(self, playlist: str, json_entry: Dict) -> bool:
        """Check if a playlist is appropriate for the JSON entry type"""
        # This would need to be customized based on the specific JSON structure
        # For now, return True to allow all matches
        return True

    def match_videos_to_json(self, videos: List[Dict], json_entries: List[Dict]) -> List[Dict]:
        """Match a list of videos to JSON entries"""
        matches = []
        
        for video in videos:
            match, score = self.find_best_match(video, json_entries)
            if match:
                match_info = {
                    'video': video,
                    'json_entry': match,
                    'confidence': score,
                    'video_url': video.get('url', ''),
                    'match_type': 'automatic' if score >= 90 else 'fuzzy'
                }
                matches.append(match_info)
                logger.info(f"Matched '{video.get('title', '')}' with confidence {score:.1f}")
            else:
                logger.warning(f"No match found for: {video.get('title', '')}")
        
        return matches

    def get_playlist_specific_videos(self, all_videos: List[Dict], target_playlists: List[str]) -> List[Dict]:
        """Filter videos from specific playlists"""
        return [v for v in all_videos if v.get('playlist') in target_playlists]

if __name__ == "__main__":
    # Test the matching algorithm
    matcher = TitleMatcher()
    
    # Example test
    test_video_title = "試玩毛EP06《哈利波腎》｜試當真"
    test_json_title = "試玩毛EP06《哈利波腎》"
    test_json_full = "試玩毛EP06《哈利波腎》｜試當真"
    
    score = matcher.calculate_match_score(test_video_title, test_json_title, test_json_full)
    print(f"Test match score: {score}")
    
    cleaned = matcher.clean_title(test_video_title)
    print(f"Cleaned title: '{cleaned}'")