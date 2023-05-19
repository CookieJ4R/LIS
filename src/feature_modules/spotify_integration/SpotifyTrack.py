import dataclasses


@dataclasses.dataclass
class SpotifyTrack:
    """
    Class representing a singular Spotify Track.
    """

    title: str
    artist: str
    cover_url: str

    def __eq__(self, other):
        if isinstance(other, SpotifyTrack):
            return self.title == other.title and self.artist == other.artist and self.cover_url == other.cover_url
        return False

    def __hash__(self):
        return hash((self.title, self.artist, self.cover_url))
