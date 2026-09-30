#!/usr/bin/env python3
# Script to build a knowledge base of past shows and music profile from KZSU API

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration for the KZSU API
BASE_URL = "https://zookeeper.stanford.edu/api/v2/"
API_KEY = "b3fcd72414bde44530b5fd7b585aaafc08ca41b1"  # Replace with actual API key
DJ_ID = '1428'

# Configuration for data storage
OUTPUT_FILE = "knowledge_base.json"

# Function to filter knowledge base by DJ (airname)
def filter_by_dj(knowledge_base, dj_name):
    filtered_show_history = []
    for playlist_entry in knowledge_base["show_history"]:
        if playlist_entry["playlist"]["airname"] == dj_name:
            filtered_show_history.append(playlist_entry)
    return {
        "metadata": knowledge_base["metadata"],
        "show_history": filtered_show_history
    }


# Set up headers for authentication
headers = {
    "X-APIKEY": API_KEY,
    "Content-Type": "application/json"
}

def get_playlists():
    """Retrieve playlists from the KZSU API"""
    url = f"{BASE_URL}playlist"
    params = {
        "filter[date]": "onNow",  # You can modify this to retrieve past playlists by date
        "page[size]": 100,  # Adjust page size as needed
        "sort": "-date"  # Sort by most recent first
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        playlists_data = response.json()
        
        print(f"Retrieved {len(playlists_data['data'])} playlists")
        return playlists_data
    except Exception as e:
        print(f"Error retrieving playlists: {e}")
        return None

def get_reviews(album_id):
    """Retrieve reviews for a specific album"""
    url = f"{BASE_URL}album/{album_id}/reviews"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"Error retrieving reviews for album {album_id}: {e}")
        return []

def get_playlist_events(playlist_id):
    """Get events associated with a playlist"""
    url = f"{BASE_URL}playlist/{playlist_id}/events"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"Error retrieving events for playlist {playlist_id}: {e}")
        return []

def build_knowledge_base():
    """Build a knowledge base of past shows and music profile"""
    playlists = get_playlists()
    
    if not playlists:
        print("No playlists retrieved. Exiting.")
        return
    
    # Extract information from each playlist
    knowledge_base = {
        "metadata": {
            "source": "KZSU Library Show API",
            "timestamp": datetime.now().isoformat(),
            "total_playlists": len(playlists["data"])
        },
        "show_history": []
    }
    
    for playlist in playlists["data"]:
        # Extract basic playlist information
        playlist_info = {
            "id": playlist["id"],
            "name": playlist.get("name", "Unknown"),
            "date": playlist.get("date"),
            "time": playlist.get("time"),
            "airname": playlist.get("airname", "Unknown"),
            "rebroadcast": playlist.get("rebroadcast", False)
        }
        
        # Get events (tracks) in the playlist
        events = get_playlist_events(playlist["id"])
        track_data = []
        for event in events:
            album_id = event["relationships"]["album"]["data"]["id"] if "album" in event.get("relationships", {}) else None
            
            # Get reviews for this album (if available)
            reviews = get_reviews(album_id) if album_id else []
            
            track_info = {
                "event_id": event["id"],
                "title": event.get("attributes", {}).get("title", "Unknown Title"),
                "artist": event.get("attributes", {}).get("artist", "Unknown Artist"),
                "album": event.get("attributes", {}).get("album", "Unknown Album"),
                "label": event.get("attributes", {}).get("label", "Unknown Label"),
                "genre": event.get("attributes", {}).get("genre", []),
                "duration": event.get("attributes", {}).get("duration", 0),
                "album_reviews": [review["attributes"] for review in reviews] if reviews else []
            }
            
            track_data.append(track_info)
        
        # Add playlist to knowledge base
        playlist_entry = {
            "playlist": playlist_info,
            "tracks": track_data
        }
        
        knowledge_base["show_history"].append(playlist_entry)
    
    # Save the knowledge base to a file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(knowledge_base, f, indent=2)
    
    print(f"Knowledge base saved to {OUTPUT_FILE}")
    print(f"Total playlists processed: {len(knowledge_base['show_history'])}")
    
if __name__ == "__main__":
    build_knowledge_base()