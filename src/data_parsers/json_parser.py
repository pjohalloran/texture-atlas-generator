import json
from typing import Any, Dict

from atlas.atlas_data import AtlasData
from atlas.texture import Texture
from data_parsers.parser import Parser

TYPES = {'AtlasData': AtlasData, 'Texture': Texture}


class CustomTypeEncoder(json.JSONEncoder):
    """A custom JSONEncoder class that knows how to encode core custom
    objects.

    Custom objects are encoded as JSON object literals (ie, dicts) with
    one key, '__TypeName__' where 'TypeName' is the actual name of the
    type to which the object belongs.  That single key maps to another
    object literal which is just the __dict__ of the object encoded."""

    def default(self, obj: Any) -> Dict[str, Any]:
        if isinstance(obj, AtlasData):
            key = 'Atlas'
            return {key: obj.__dict__}
        elif isinstance(obj, Texture):
            key = 'Image'
            return {key: obj.__dict__}
        return json.JSONEncoder.default(self, obj)


class JsonParser(Parser):

    def get_file_ext(self) -> str:
        return 'json'

    def parse(self, atlas_data: AtlasData) -> None:
        self.parser_output = json.dumps(atlas_data, cls=CustomTypeEncoder, indent=4)
