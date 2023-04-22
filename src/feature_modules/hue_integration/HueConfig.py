class HueConfig:
    """
    Configuration object for the philipps hue integration to pass to sub-modules.
    """
    def __init__(self, bridge_ip: str, client_key: str):
        self.bridge_ip = bridge_ip
        self.client_key = client_key
