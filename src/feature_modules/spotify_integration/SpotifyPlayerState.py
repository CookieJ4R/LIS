import dataclasses
import json
from enum import Enum, auto

from feature_modules.spotify_integration.SpotifyTrack import SpotifyTrack


class SpotifyPlayback(str, Enum):
    """
    Enum representing the different playback states
    """
    NONE = auto()
    PLAYING = auto()
    STOPPED = auto()


@dataclasses.dataclass
class SpotifyPlayerState:
    """
    Class representing the current status of the player. Provides access to the track currently being played as well
    as to the playback state.
    """

    playback: SpotifyPlayback
    current_track: SpotifyTrack

    def to_json(self):
        """
        Helper method to get a json representation of the player state for the api response.
        :return: the json representation of the player state.
        """
        return json.dumps({"playback": self.playback, "current_track": self.current_track.__dict__})
