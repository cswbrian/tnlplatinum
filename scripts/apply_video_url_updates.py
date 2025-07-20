#!/usr/bin/env python3
"""
Apply video URL updates to films.json based on cross-reference results.

This script takes the high-confidence matches from the cross-reference analysis
and applies the video URLs to the films.json file.
"""

import json
import os
from typing import List, Dict

def load_cross_reference_results(filepath: str) -> Dict:
    """Load cross-reference results from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def apply_updates(films_file: str, results: Dict, min_confidence: float = 0.9) -> int:
    """Apply video URL updates to films.json for high-confidence matches."""
    
    # Load films.json
    with open(films_file, 'r', encoding='utf-8') as f:
        films = json.load(f)
    
    # Get high-confidence matches
    high_confidence_matches = [
        match for match in results['all_matches'] 
        if match['confidence'] >= min_confidence
    ]
    
    print(f"Found {len(high_confidence_matches)} high-confidence matches (>= {min_confidence})")
    
    updates_made = 0
    
    # Apply updates
    for match in high_confidence_matches:
        film_title = match['film_title']
        video_url = match['video_url']
        
        # Find the film in the films array
        for i, film in enumerate(films):
            if (film.get('title') == film_title and 
                not film.get('videoUrl')):  # Only update if no existing URL
                
                print(f"Updating film: '{film_title}'")
                print(f"  Adding videoUrl: {video_url}")
                
                films[i]['videoUrl'] = video_url
                updates_made += 1
                break
    
    if updates_made > 0:
        # Create backup
        backup_file = films_file + '.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(films, f, ensure_ascii=False, indent=2)
        print(f"Created backup: {backup_file}")
        
        # Save updated films.json
        with open(films_file, 'w', encoding='utf-8') as f:
            json.dump(films, f, ensure_ascii=False, indent=2)
        
        print(f"Updated {updates_made} films in {films_file}")
    else:
        print("No updates were needed.")
    
    return updates_made

def main():
    """Main function."""
    data_dir = "/Users/yellowcandle/dev/tnlplatinum/src/data"
    results_file = "/Users/yellowcandle/dev/tnlplatinum/scripts/film_cross_reference_results.json"
    films_file = os.path.join(data_dir, "films.json")
    
    # Load results
    results = load_cross_reference_results(results_file)
    
    print("Cross-reference Analysis Summary:")
    print(f"  Total films: {results['summary']['total_films']}")
    print(f"  Films with URL: {results['summary']['films_with_url']}")
    print(f"  Films without URL: {results['summary']['films_without_url']}")
    print(f"  Potential matches found: {results['summary']['total_matches_found']}")
    print()
    
    print("Confidence breakdown:")
    print(f"  High confidence (≥0.9): {results['confidence_breakdown']['high_confidence']}")
    print(f"  Medium confidence (0.8-0.89): {results['confidence_breakdown']['medium_confidence']}")
    print(f"  Low confidence (0.6-0.79): {results['confidence_breakdown']['low_confidence']}")
    print()
    
    # Show all matches for review
    print("All matches found:")
    for i, match in enumerate(results['all_matches'], 1):
        confidence = match['confidence']
        source = match['source']
        film_title = match['film_title']
        video_url = match['video_url']
        
        print(f"{i:2d}. [{confidence:.3f}] {source}: '{film_title}'")
        print(f"    URL: {video_url}")
        
        if confidence >= 0.9:
            print("    -> HIGH CONFIDENCE - Will be automatically applied")
        elif confidence >= 0.8:
            print("    -> MEDIUM CONFIDENCE - Review recommended")
        else:
            print("    -> LOW CONFIDENCE - Manual verification needed")
        print()
    
    # Apply high-confidence updates
    if results['confidence_breakdown']['high_confidence'] > 0:
        print("=" * 60)
        print("APPLYING HIGH-CONFIDENCE UPDATES")
        print("=" * 60)
        updates_made = apply_updates(films_file, results, min_confidence=0.9)
        
        if updates_made > 0:
            print(f"\nSuccessfully applied {updates_made} video URL updates!")
            print(f"Films.json has been updated.")
            print(f"A backup was created as films.json.backup")
        else:
            print("\nNo updates were applied.")
    else:
        print("No high-confidence matches to apply.")

if __name__ == "__main__":
    main()