"""
DJ Stace Agent - Simple implementation per agents.md / instructions.md
Hybrid start: basic agent functions + knowledge base integration
"""

import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("KZSU_LIBRARY_API_KEY", "b3fcd72414bde44530b5fd7b585aaafc08ca41b1")
BASE_URL = "https://zookeeper.stanford.edu/api/v2/"
BASE_URL_V1 = "https://zookeeper.stanford.edu/api/v1/"

HEADERS = {"X-APIKEY": API_KEY, "Content-Type": "application/json"}

def initialize_show_preparation():
    print("[1] Initializing show preparation...")
    # Auth check
    try:
        r = requests.get(f"{BASE_URL}playlist?filter[date]=onNow&page[size]=1", headers=HEADERS)
        r.raise_for_status()
        print("   API connection OK")
        return {"status": "ready", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"   API error: {e}")
        return {"status": "error", "error": str(e)}

def get_tracklist_from_library(filter_date="onNow", page_size=100):
    print("[2] Fetching tracklist from library database...")
    url = f"{BASE_URL}playlist"
    params = {"filter[date]": filter_date, "page[size]": page_size}
    r = requests.get(url, headers=HEADERS, params=params)
    r.raise_for_status()
    data = r.json()
    print(f"   Retrieved {len(data.get('data', []))} playlists")
    return data

def get_weather_data(location="San Francisco"):
    print("[3] Fetching weather data...")
    # Placeholder - requires WEATHER_API_KEY
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("   WEATHER_API_KEY not set, returning mock data")
        return {"location": location, "temp_c": 18, "condition": "Partly cloudy", "mock": True}
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def generate_playlist_recommendations(weather_data, tracklist):
    print("[4] Generating playlist recommendations...")
    # Simple heuristic: use knowledge base
    kb_path = os.path.join(os.path.dirname(__file__), "../../knowledge_base.json")
    try:
        with open(kb_path) as f:
            kb = json.load(f)
        # Count artists
        from collections import Counter
        artists = []
        for show in kb.get("show_history", []):
            for t in show.get("tracks", []):
                if t.get("artist"):
                    artists.append(t["artist"])
        top = Counter(artists).most_common(5)
        print(f"   Top artists from history: {top}")
        return {"weather": weather_data, "top_artists": top, "recommendations": "based on history + weather"}
    except Exception as e:
        print(f"   Knowledge base error: {e}")
        return {"weather": weather_data, "recommendations": "fallback"}

def schedule_social_media_posts(playlist_recommendations):
    print("[5] Scheduling social media posts...")
    api_key = os.getenv("SOCIAL_MEDIA_API_KEY")
    if not api_key:
        print("   SOCIAL_MEDIA_API_KEY not set, dry-run")
        return {"status": "dry_run", "recommendations": playlist_recommendations}
    # Placeholder
    return {"status": "scheduled", "count": 1}

def monitor_show_performance():
    print("[6] Monitoring show performance...")
    # Placeholder analytics
    return {"listeners": 0, "song_plays": 0, "status": "mock"}

def compile_post_show_report():
    print("[7] Compiling post-show report...")
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": "Post-show report compiled from knowledge base and mock metrics"
    }
    return report

if __name__ == "__main__":
    initialize_show_preparation()
    tl = get_tracklist_from_library("onNow", 1)
    weather = get_weather_data()
    recs = generate_playlist_recommendations(weather, tl)
    schedule_social_media_posts(recs)
    monitor_show_performance()
    compile_post_show_report()
    print("\nWorkflow complete.")
