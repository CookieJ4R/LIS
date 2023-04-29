"""
This files contains all Events used by the Spotify feature module.
"""
from core_modules.eventing.BaseEvent import BaseEvent
from core_modules.scheduling.SimpleSchedulableEvent import SimpleSchedulableEvent
from feature_modules.spotify_integration.SpotifyPlaybackState import SpotifyPlaybackState


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

    def __init__(self, playback_state: SpotifyPlaybackState):
        self.playback_state = playback_state
