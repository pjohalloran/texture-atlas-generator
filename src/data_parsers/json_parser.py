import simplejson

from parser import Parser


class JsonParser(Parser):
    json_data = None

    def __init__(self, atlas_data):
        super.__init__(self, atlas_data)

    def parse(self):
        self.json_data = simplejson.dumps(self.atlas_data)
