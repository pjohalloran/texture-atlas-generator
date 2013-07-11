import xml.dom.minidom

from parser import Parser


class XmlParser(Parser):
    document = None
    root_element = None

    def get_file_ext(self):
        return 'xml'

    def parse(self, atlas_data):
        self._create_root_node()
        self._parse_atlas_data(atlas_data)
        self.parser_output = self.document.toprettyxml(newl="\n", indent="    ")
        self._clean_up()

    def _create_root_node(self, root_name='Root'):
        self.document = xml.dom.minidom.Document()
        self.root_element = self.document.createElement(root_name)
        self.document.appendChild(self.root_element)

    def _parse_atlas_data(self, atlas_data):
        for key in atlas_data.texture_dict:
            self._add_element(atlas_data.texture_dict[key].to_dict())

    def _add_element(self, attribute_dict):
        element = self.document.createElement('Image')
        for key in attribute_dict.keys():
            element.setAttribute(key, str(attribute_dict[key]))
        self.root_element.appendChild(element)

    def _clean_up(self):
        self.document.unlink()
        self.document = None
