# Instructions for DJ Stace Agent

## General Configuration

### Environment Setup
1. Install Python 3.9 or higher
2. Create a virtual environment:
   ```bash
   python3.9 -m venv kzsudjstace_env
   source kzsudjstace_env/bin/activate
   ```
3. Install required dependencies:
   ```bash
   pip install requests json datetime time
   ```
4. Set up environment variables:
   ```bash
   export KZSU_LIBRARY_API_KEY=b3fcd72414bde44530b5fd7b585aaafc08ca41b1
   export WEATHER_API_KEY=your_weather_api_key_here
   export SOCIAL_MEDIA_API_KEY=your_social_media_api_key_here
   ```

## Show Preparation Workflow

### Step 1: Initialize Show Preparation
- Call the `initialize_show_preparation()` function to start the show preparation process.
- This function will set up all necessary configurations and authenticate with required APIs.

### Step 2: Retrieve Tracklist Information
- Use the `get_tracklist_from_library()` function to fetch the current tracklist from the library database.
- This function requires authentication and returns a JSON object containing track information.

### Step 3: Fetch Weather Data
- Call the `get_weather_data(location="San Francisco")` function to retrieve current weather conditions.
- The function returns a JSON object with temperature, humidity, wind speed, and other relevant data.

### Step 4: Generate Playlist Recommendations
- Use the `generate_playlist_recommendations(weather_data, tracklist)` function to create playlist recommendations based on current weather conditions.
- This function takes weather data and tracklist as input and returns a list of recommended tracks.

### Step 5: Schedule Social Media Posts
- Call the `schedule_social_media_posts(playlist_recommendations)` function to schedule posts for social media platforms.
- The function requires playlist recommendations as input and returns confirmation of successful scheduling.

### Step 6: Monitor Show Performance
- Use the `monitor_show_performance()` function to track show performance metrics in real-time.
- This function provides live updates on listener count, song plays, and other key metrics.

### Step 7: Compile Post-Show Report
- Call the `compile_post_show_report()` function to generate a comprehensive post-show report.
- The function gathers all relevant data from previous steps and compiles it into a formatted report.