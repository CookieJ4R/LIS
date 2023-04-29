import dataclasses


@dataclasses.dataclass
class SpotifyTrack:
    """
    Class representing a singular Spotify Track.
    """

    title: str
    artist: str
    cover_url: str
