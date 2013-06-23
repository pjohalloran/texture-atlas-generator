import simplejson

from parser import Parser
from atlas.atlas_data import AtlasData
from atlas.texture import Texture

TYPES = {'AtlasData': AtlasData, 'Texture': Texture}


class CustomTypeEncoder(simplejson.JSONEncoder):
    """A custom JSONEncoder class that knows how to encode core custom
    objects.

    Custom objects are encoded as JSON object literals (ie, dicts) with
    one key, '__TypeName__' where 'TypeName' is the actual name of the
    type to which the object belongs.  That single key maps to another
    object literal which is just the __dict__ of the object encoded."""

    def default(self, obj):
        if isinstance(obj, AtlasData):
            key = 'Atlas'
            return {key: obj.__dict__}
        elif isinstance(obj, Texture):
            key = 'Image'
            return {key: obj.__dict__}
        return simplejson.JSONEncoder.default(self, obj)


class JsonParser(Parser):

    def get_file_ext(self):
        return 'json'

    def parse(self, atlas_data):
        self.parser_output = simplejson.dumps(atlas_data, cls=CustomTypeEncoder, indent=4)
