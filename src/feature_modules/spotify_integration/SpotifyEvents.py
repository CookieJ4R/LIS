"""
This files contains all Events used by the Spotify feature module.
"""
from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.SimpleSchedulableEvent import SimpleSchedulableEvent
from feature_modules.spotify_integration.SpotifyPlayerState import SpotifyPlayerState


class SpotifyPausePlaybackEvent(BaseEvent, SimpleSchedulableEvent):
    """
    Event to pause the current spotify playback
    """
    ...


class SpotifyStartResumePlaybackEvent(BaseEvent, SimpleSchedulableEvent):
    """
    Event to start or resume the current spotify playback
    """
    ...


class SpotifyNextTrackEvent(BaseEvent, SimpleSchedulableEvent):
    """
    Event to switch to the next spotify track
    """
    ...


class SpotifyPreviousTrackEvent(BaseEvent, SimpleSchedulableEvent):
    """
    Event to switch to the previous spotify track
    """
    ...


class SpotifyGetCurrentTrackEvent(BaseEvent):
    """
    Event to get the current playing track and the playback state
    """
    ...


class SpotifyGetCurrentTrackResponseEvent(BaseEvent):
    """
    Event to act as a response to the SpotifyGetCurrentTrackEvent
    """
    def __init__(self, playback_state: SpotifyPlayerState):
        self.playback_state = playback_state

    def __eq__(self, other):
        if isinstance(other, SpotifyGetCurrentTrackResponseEvent):
            return self.playback_state == other.playback_state
        return False

    def __hash__(self):
        return hash(self.playback_state)
