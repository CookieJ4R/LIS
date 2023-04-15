"""
File containing all the Events used by the HueInteractor and HueApi
"""
from core_modules.eventing.BaseEvent import BaseEvent


class HueLampSetStateEvent(BaseEvent):
    """
    Event for changing the on/off state of a specific lamp.
    """
    def __init__(self, lamp_id: str, on: bool):
        self.lamp_id = lamp_id
        self.on = on
