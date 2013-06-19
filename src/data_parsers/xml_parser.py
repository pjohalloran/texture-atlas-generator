import xml.dom.minidom

from parser import Parser


class XmlParser(Parser):
    document = None
    root_element = None

    def __init__(self, atlas_data):
        super.__init__(self, atlas_data)

    def parse(self):
        self._create_root_node()
        # TODO: Parse atlas and generate document from atlas_data
        self._parse_atlas_data()
        self.parser_output = self.document.toprettyxml(newl="\n", indent="    ")
        self._clean_up()

    def _create_root_node(self, root_name='Root'):
        self._clean_up()
        self.document = xml.dom.minidom.Document()
        self.root_element = self.document.createElement(root_name)
        self.document.appendChild(self.root_element)

    def _parse_atlas_data(self):
        for key in self.atlas_data.texture_dict:
            self._add_element(key, self.atlas_data.texture_dict[key].to_dict())

    def _add_element(self, element_name, attribute_dict):
        self.document.createElement(element_name)
        for key in attribute_dict.keys():
            self.document.set_attribute(key, attribute_dict[key])

    def _clean_up(self):
        self.document.unlink()
        self.document = None
