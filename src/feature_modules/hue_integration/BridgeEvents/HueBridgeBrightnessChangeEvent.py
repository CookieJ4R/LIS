import dataclasses
import json

from feature_modules.hue_integration.BridgeEvents.HueBridgeBaseEvent import HueBridgeBaseEvent


@dataclasses.dataclass
class HueBridgeBrightnessChangeEvent(HueBridgeBaseEvent):
    """
    This class represents the HueBridge event that gets sent when the brightness of a light changes.
    """
    id: str
    brightness: float

    @staticmethod
    def from_dict(json_parsed_obj: dict):
        return HueBridgeBrightnessChangeEvent(json_parsed_obj["id"], json_parsed_obj["dimming"]["brightness"])

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
