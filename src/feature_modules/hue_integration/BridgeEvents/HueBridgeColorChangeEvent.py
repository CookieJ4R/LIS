import dataclasses
import json

from feature_modules.hue_integration.BridgeEvents.HueBridgeBaseEvent import HueBridgeBaseEvent


@dataclasses.dataclass
class HueBridgeColorChangeEvent(HueBridgeBaseEvent):
    """
    This class represents the HueBridge event that gets sent when the color of a light changes.
    """
    id: str
    color_x: float
    color_y: float
    color_temp_mirek: int
    color_temp_mirek_valid: bool

    @staticmethod
    def from_dict(json_parsed_obj: dict):
        return HueBridgeColorChangeEvent(json_parsed_obj["id"],
                                         json_parsed_obj["color"]["xy"]["x"],
                                         json_parsed_obj["color"]["xy"]["y"],
                                         json_parsed_obj["color_temperature"]["mirek"],
                                         json_parsed_obj["color_temperature"]["mirek_valid"]
                                         )

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
