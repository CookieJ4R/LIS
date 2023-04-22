import dataclasses
import json

from feature_modules.hue_integration.BridgeEvents.HueBridgeBaseEvent import HueBridgeBaseEvent


@dataclasses.dataclass
class HueBridgeStateChangeEvent(HueBridgeBaseEvent):
    """
    This class represents the HueBridge event that gets sent when the state of a light changes.
    """
    id: str
    on: bool

    @staticmethod
    def from_dict(json_parsed_obj: dict):
        return HueBridgeStateChangeEvent(json_parsed_obj["id"], json_parsed_obj["on"]["on"])

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
