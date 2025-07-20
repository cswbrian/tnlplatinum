#!/usr/bin/env python3
"""
Cross-reference films.json with other JSON files to find video URLs.

This script:
1. Loads all JSON files from the data directory
2. Finds films.json entries without videoUrl
3. Searches other JSON files for matching titles/fullTitles
4. Creates mappings with confidence scores for fuzzy matching
5. Shows potential matches that can provide video URLs
"""

import json
import os
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Any, Optional
import re

def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    """Load and return JSON data from file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def normalize_title(title: str) -> str:
    """Normalize title for better matching."""
    if not title:
        return ""
    
    normalized = title.strip()
    
    # Remove common prefixes and suffixes, preserving the core title
    patterns_to_extract = [
        r'試映劇場《(.+?)》',
        r'試音片《(.+?)》',
        r'試乜都得《(.+?)》',
        r'試玩毛[^《]*《(.+?)》',
        r'《(.+?)》',
    ]
    
    # Try to extract the core title
    for pattern in patterns_to_extract:
        match = re.search(pattern, normalized)
        if match:
            normalized = match.group(1)
            break
    
    # Remove trailing text after common delimiters
    normalized = re.split(r'[｜\|]', normalized)[0]
    normalized = re.split(r'- YouTube', normalized)[0]
    normalized = re.split(r'- youtube', normalized, flags=re.IGNORECASE)[0]
    
    # Clean up extra whitespace and special characters
    normalized = re.sub(r'\s+', ' ', normalized)
    normalized = normalized.strip('《》[]()｜|：:')
    
    return normalized.strip()

def calculate_similarity(str1: str, str2: str, debug=False) -> float:
    """Calculate similarity between two strings."""
    if not str1 or not str2:
        return 0.0
    
    # Filter out meaningless strings
    if str2 in ['／', '/', '-', '', ' '] or len(str2.strip()) < 2:
        return 0.0
    
    # Direct match
    if str1 == str2:
        return 1.0
    
    # Normalize both strings
    norm1 = normalize_title(str1)
    norm2 = normalize_title(str2)
    
    # Filter out empty normalized strings
    if not norm1 or not norm2 or len(norm1.strip()) < 2 or len(norm2.strip()) < 2:
        return 0.0
    
    if debug:
        print(f"  Comparing: '{norm1}' vs '{norm2}'")
    
    if norm1 == norm2:
        return 0.95
    
    # Use SequenceMatcher for fuzzy matching
    similarity = SequenceMatcher(None, norm1.lower(), norm2.lower()).ratio()
    
    # Boost score if one string contains the other (with length checks)
    if (norm1.lower() in norm2.lower() or norm2.lower() in norm1.lower()) and min(len(norm1), len(norm2)) >= 3:
        similarity = max(similarity, 0.8)
    
    # Additional fuzzy matching strategies
    # Check if they're very similar after removing spaces and special characters
    clean1 = re.sub(r'[^\w]', '', norm1.lower())
    clean2 = re.sub(r'[^\w]', '', norm2.lower())
    
    if clean1 == clean2 and len(clean1) >= 3:
        similarity = max(similarity, 0.9)
    elif (clean1 in clean2 or clean2 in clean1) and min(len(clean1), len(clean2)) >= 3:
        similarity = max(similarity, 0.85)
    
    if debug:
        print(f"    Similarity: {similarity:.3f}")
    
    return similarity

def find_matches(films_without_url: List[Dict], other_data: List[Dict], 
                source_name: str, min_confidence: float = 0.6, debug_film: str = None) -> List[Dict]:
    """Find potential matches between films and other data sources."""
    matches = []
    
    for film in films_without_url:
        film_title = film.get('title', '')
        film_full_title = film.get('fullTitle', '')
        
        # Debug specific film
        debug_this_film = debug_film and (debug_film in film_title or debug_film in film_full_title)
        if debug_this_film:
            print(f"\n=== DEBUGGING FILM: {film_title} ===")
            print(f"Full title: {film_full_title}")
        
        best_matches = []
        
        for item in other_data:
            # Get title fields from the other data source
            other_title = item.get('title', '')
            other_full_title = item.get('fullTitle', '')
            other_song = item.get('song', '')  # For songs.json
            other_movie = item.get('movie', '')  # For songs.json
            
            # Only consider items with videoUrl
            if not item.get('videoUrl'):
                continue
            
            if debug_this_film:
                print(f"\nChecking against: {other_title}")
                if other_full_title:
                    print(f"  Full: {other_full_title}")
            
            # Calculate similarities for different field combinations
            similarities = []
            
            # Compare film title with other title
            if film_title and other_title:
                sim = calculate_similarity(film_title, other_title, debug_this_film)
                similarities.append(('title_to_title', sim))
            
            # Compare film title with other fullTitle
            if film_title and other_full_title:
                sim = calculate_similarity(film_title, other_full_title, debug_this_film)
                similarities.append(('title_to_fullTitle', sim))
            
            # Compare film fullTitle with other title
            if film_full_title and other_title:
                sim = calculate_similarity(film_full_title, other_title, debug_this_film)
                similarities.append(('fullTitle_to_title', sim))
            
            # Compare film fullTitle with other fullTitle
            if film_full_title and other_full_title:
                sim = calculate_similarity(film_full_title, other_full_title, debug_this_film)
                similarities.append(('fullTitle_to_fullTitle', sim))
            
            # For songs.json, also compare with song and movie fields
            if source_name == 'songs':
                if film_title and other_song:
                    sim = calculate_similarity(film_title, other_song, debug_this_film)
                    similarities.append(('title_to_song', sim))
                
                if film_title and other_movie:
                    sim = calculate_similarity(film_title, other_movie, debug_this_film)
                    similarities.append(('title_to_movie', sim))
            
            # Get the best similarity score
            if similarities:
                best_sim_type, best_sim_score = max(similarities, key=lambda x: x[1])
                
                if best_sim_score >= min_confidence:
                    best_matches.append({
                        'film': film,
                        'match': item,
                        'source': source_name,
                        'confidence': best_sim_score,
                        'match_type': best_sim_type,
                        'film_title': film_title,
                        'film_full_title': film_full_title,
                        'match_title': other_title,
                        'match_full_title': other_full_title,
                        'video_url': item.get('videoUrl')
                    })
        
        # Sort matches by confidence and keep the best ones
        best_matches.sort(key=lambda x: x['confidence'], reverse=True)
        matches.extend(best_matches[:3])  # Keep top 3 matches per film
    
    return matches

def main():
    """Main function to execute the cross-referencing."""
    # Set up paths
    data_dir = "/Users/yellowcandle/dev/tnlplatinum/src/data"
    
    # Load all JSON files
    print("Loading JSON files...")
    films = load_json_file(os.path.join(data_dir, "films.json"))
    ads = load_json_file(os.path.join(data_dir, "ads.json"))
    variety_shows = load_json_file(os.path.join(data_dir, "variety-shows.json"))
    audition_films = load_json_file(os.path.join(data_dir, "audition-films.json"))
    songs = load_json_file(os.path.join(data_dir, "songs.json"))
    
    print(f"Loaded {len(films)} films, {len(ads)} ads, {len(variety_shows)} variety shows, "
          f"{len(audition_films)} audition films, {len(songs)} songs")
    
    # Find films without videoUrl
    films_without_url = [film for film in films if not film.get('videoUrl')]
    films_with_url = [film for film in films if film.get('videoUrl')]
    
    print(f"\nFilms status:")
    print(f"  - With videoUrl: {len(films_with_url)}")
    print(f"  - Without videoUrl: {len(films_without_url)}")
    print(f"  - Total films: {len(films)}")
    
    # Find matches in each data source
    print(f"\nSearching for matches...")
    
    # Debug specific film (uncomment to debug)
    debug_film = None  # Set to None to disable debugging
    
    all_matches = []
    
    # Search in ads
    ads_matches = find_matches(films_without_url, ads, 'ads', min_confidence=0.6, debug_film=debug_film)
    all_matches.extend(ads_matches)
    print(f"Found {len(ads_matches)} potential matches in ads.json")
    
    # Search in variety shows
    variety_matches = find_matches(films_without_url, variety_shows, 'variety-shows', min_confidence=0.6, debug_film=debug_film)
    all_matches.extend(variety_matches)
    print(f"Found {len(variety_matches)} potential matches in variety-shows.json")
    
    # Search in audition films
    audition_matches = find_matches(films_without_url, audition_films, 'audition-films', min_confidence=0.6, debug_film=debug_film)
    all_matches.extend(audition_matches)
    print(f"Found {len(audition_matches)} potential matches in audition-films.json")
    
    # Search in songs
    songs_matches = find_matches(films_without_url, songs, 'songs', min_confidence=0.6, debug_film=debug_film)
    all_matches.extend(songs_matches)
    print(f"Found {len(songs_matches)} potential matches in songs.json")
    
    # Sort all matches by confidence
    all_matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    print(f"\nTotal potential matches found: {len(all_matches)}")
    
    # Group matches by confidence level
    high_confidence = [m for m in all_matches if m['confidence'] >= 0.9]
    medium_confidence = [m for m in all_matches if 0.8 <= m['confidence'] < 0.9]
    low_confidence = [m for m in all_matches if 0.6 <= m['confidence'] < 0.8]
    
    print(f"\nConfidence breakdown:")
    print(f"  - High confidence (≥0.9): {len(high_confidence)}")
    print(f"  - Medium confidence (0.8-0.89): {len(medium_confidence)}")
    print(f"  - Low confidence (0.6-0.79): {len(low_confidence)}")
    
    # Display detailed results
    print(f"\n{'='*80}")
    print("DETAILED MATCH RESULTS")
    print('='*80)
    
    for category, matches in [
        ("HIGH CONFIDENCE MATCHES (≥0.9)", high_confidence),
        ("MEDIUM CONFIDENCE MATCHES (0.8-0.89)", medium_confidence),
        ("LOW CONFIDENCE MATCHES (0.6-0.79)", low_confidence)
    ]:
        if matches:
            print(f"\n{category}")
            print("-" * len(category))
            
            for i, match in enumerate(matches[:20], 1):  # Show top 20 per category
                print(f"\n{i}. CONFIDENCE: {match['confidence']:.3f} | SOURCE: {match['source']}")
                print(f"   FILM TITLE: '{match['film_title']}'")
                if match['film_full_title']:
                    print(f"   FILM FULL TITLE: '{match['film_full_title']}'")
                print(f"   MATCH TITLE: '{match['match_title']}'")
                if match['match_full_title']:
                    print(f"   MATCH FULL TITLE: '{match['match_full_title']}'")
                print(f"   MATCH TYPE: {match['match_type']}")
                print(f"   VIDEO URL: {match['video_url']}")
                
                # Show additional fields for songs
                if match['source'] == 'songs' and match['match'].get('song'):
                    print(f"   SONG: '{match['match']['song']}'")
                if match['source'] == 'songs' and match['match'].get('movie'):
                    print(f"   MOVIE: '{match['match']['movie']}'")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print('='*80)
    
    # Count unique films that have matches
    unique_films_with_matches = len(set(match['film']['title'] for match in all_matches))
    
    print(f"Films without videoUrl: {len(films_without_url)}")
    print(f"Films with potential matches: {unique_films_with_matches}")
    print(f"Coverage improvement potential: {unique_films_with_matches}/{len(films_without_url)} ({unique_films_with_matches/len(films_without_url)*100:.1f}%)")
    
    # Show matches by source
    print(f"\nMatches by source:")
    for source in ['ads', 'variety-shows', 'audition-films', 'songs']:
        source_matches = [m for m in all_matches if m['source'] == source]
        if source_matches:
            print(f"  - {source}: {len(source_matches)} matches")
    
    # Save results to file
    results_file = "/Users/yellowcandle/dev/tnlplatinum/scripts/film_cross_reference_results.json"
    
    results = {
        'summary': {
            'total_films': len(films),
            'films_with_url': len(films_with_url),
            'films_without_url': len(films_without_url),
            'total_matches_found': len(all_matches),
            'unique_films_with_matches': unique_films_with_matches,
            'coverage_improvement_potential': f"{unique_films_with_matches}/{len(films_without_url)} ({unique_films_with_matches/len(films_without_url)*100:.1f}%)"
        },
        'confidence_breakdown': {
            'high_confidence': len(high_confidence),
            'medium_confidence': len(medium_confidence),
            'low_confidence': len(low_confidence)
        },
        'matches_by_source': {
            'ads': len([m for m in all_matches if m['source'] == 'ads']),
            'variety_shows': len([m for m in all_matches if m['source'] == 'variety-shows']),
            'audition_films': len([m for m in all_matches if m['source'] == 'audition-films']),
            'songs': len([m for m in all_matches if m['source'] == 'songs'])
        },
        'all_matches': all_matches
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return all_matches

if __name__ == "__main__":
    matches = main()