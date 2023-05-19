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

    def __eq__(self, other):
        if isinstance(other, SpotifyPlayerState):
            return self.playback == other.playback and self.current_track == other.current_track
        return False

    def __hash__(self):
        return hash((self.playback, self.current_track))
