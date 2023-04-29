import json
from enum import Enum, auto

from feature_modules.spotify_integration.SpotifyTrack import SpotifyTrack


class SpotifyPlayback(str, Enum):
    NONE = auto()
    PLAYING = auto()
    STOPPED = auto()


class SpotifyPlaybackState:

    def __init__(self, playback: [SpotifyPlayback | None], current_track: [SpotifyTrack | None]):
        self.playback = playback
        self.current_track = current_track

    def to_json(self):
        return json.dumps({"playback": self.playback, "current_track": self.current_track.__dict__})
