import requests
from config.config import Config

class PexelsSearcher:
    """Searches images and videos using Pexels API."""
    BASE_URL = "https://api.pexels.com/v1/"
    VIDEO_URL = "https://api.pexels.com/videos/"

    def __init__(self):
        self.api_key = Config.get_pexels_token()
        self.headers = {"Authorization": self.api_key}

    def search_images(self, query, per_page=3, orientation=None):
        url = f"{self.BASE_URL}search"
        params = {"query": query, "per_page": per_page}
        if orientation:
            params["orientation"] = orientation  # portrait, landscape, square
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return [photo["src"]["medium"] for photo in data.get("photos", [])]
        return []

    def search_videos(self, query, per_page=2, orientation=None):
        url = f"{self.VIDEO_URL}search"
        params = {"query": query, "per_page": per_page}
        if orientation:
            params["orientation"] = orientation  # portrait, landscape, square
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return [video["video_files"][0]["link"] for video in data.get("videos", [])]
        return []
