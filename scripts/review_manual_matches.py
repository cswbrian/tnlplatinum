#!/usr/bin/env python3
"""
Manual review tool for medium and low confidence matches.

This script helps review potential matches that need manual verification
before applying video URLs to films.json.
"""

import json
import os
from typing import List, Dict

def load_cross_reference_results(filepath: str) -> Dict:
    """Load cross-reference results from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def show_detailed_match(match: Dict, index: int):
    """Show detailed information about a match for manual review."""
    print(f"\n{'='*80}")
    print(f"MATCH #{index} - CONFIDENCE: {match['confidence']:.3f}")
    print(f"{'='*80}")
    
    print(f"SOURCE: {match['source']}")
    print(f"MATCH TYPE: {match['match_type']}")
    print()
    
    print("FILM (without video URL):")
    film = match['film']
    print(f"  Title: '{film.get('title', '')}'")
    print(f"  Full Title: '{film.get('fullTitle', '')}'")
    print(f"  Director: {film.get('director', 'N/A')}")
    print(f"  Release Date: {film.get('releaseDate', 'N/A')}")
    print()
    
    print("POTENTIAL MATCH (with video URL):")
    potential_match = match['match']
    print(f"  Title: '{potential_match.get('title', '')}'")
    print(f"  Full Title: '{potential_match.get('fullTitle', '')}'")
    print(f"  Director: {potential_match.get('director', 'N/A')}")
    print(f"  Release Date: {potential_match.get('releaseDate', 'N/A')}")
    print(f"  Video URL: {potential_match.get('videoUrl', 'N/A')}")
    
    if match['source'] == 'songs':
        print(f"  Song: '{potential_match.get('song', '')}'")
        print(f"  Movie: '{potential_match.get('movie', '')}'")

def main():
    """Main function."""
    results_file = "/Users/yellowcandle/dev/tnlplatinum/scripts/film_cross_reference_results.json"
    
    # Load results
    results = load_cross_reference_results(results_file)
    
    print("MANUAL REVIEW TOOL FOR VIDEO URL MATCHES")
    print("=" * 80)
    print()
    
    # Categorize matches
    high_confidence = [m for m in results['all_matches'] if m['confidence'] >= 0.9]
    medium_confidence = [m for m in results['all_matches'] if 0.8 <= m['confidence'] < 0.9]
    low_confidence = [m for m in results['all_matches'] if 0.6 <= m['confidence'] < 0.8]
    
    print("SUMMARY:")
    print(f"  High confidence (≥0.9): {len(high_confidence)} matches")
    print(f"  Medium confidence (0.8-0.89): {len(medium_confidence)} matches")
    print(f"  Low confidence (0.6-0.79): {len(low_confidence)} matches")
    print()
    
    print(f"High-confidence matches have been automatically applied.")
    print(f"The following matches require manual review:")
    
    # Review medium confidence matches
    if medium_confidence:
        print(f"\n{'='*80}")
        print("MEDIUM CONFIDENCE MATCHES (0.8-0.89)")
        print("These are likely correct but should be verified:")
        print(f"{'='*80}")
        
        for i, match in enumerate(medium_confidence, 1):
            show_detailed_match(match, i)
    
    # Review low confidence matches
    if low_confidence:
        print(f"\n{'='*80}")
        print("LOW CONFIDENCE MATCHES (0.6-0.79)")
        print("These need careful verification:")
        print(f"{'='*80}")
        
        for i, match in enumerate(low_confidence, len(medium_confidence) + 1):
            show_detailed_match(match, i)
    
    # Provide recommendations
    print(f"\n{'='*80}")
    print("RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if medium_confidence:
        print("\nMEDIUM CONFIDENCE MATCHES:")
        for i, match in enumerate(medium_confidence, 1):
            film_title = match['film']['title']
            video_url = match['video_url']
            print(f"  {i}. '{film_title}'")
            print(f"     Video URL: {video_url}")
            print(f"     Recommendation: Likely correct - verify titles and apply manually")
    
    if low_confidence:
        print("\nLOW CONFIDENCE MATCHES:")
        for i, match in enumerate(low_confidence, 1):
            film_title = match['film']['title']
            video_url = match['video_url']
            print(f"  {i}. '{film_title}'")
            print(f"     Video URL: {video_url}")
            print(f"     Recommendation: Needs verification - may be false positive")
    
    print(f"\nTo apply a match manually:")
    print(f"1. Verify the match is correct by checking the video content")
    print(f"2. Edit films.json directly to add the videoUrl field")
    print(f"3. Or use the apply_video_url_updates.py script with a lower confidence threshold")

if __name__ == "__main__":
    main()