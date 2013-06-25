import os.path
import shutil

from data_parsers.json_parser import JsonParser
from data_parsers.xml_parser import XmlParser
from data_parsers.parser import ParserError


def get_parser(parser_type):
    if parser_type == 'xml':
        return XmlParser()
    elif parser_type == 'json':
        return JsonParser()
    else:
        raise ParserError('Unknown parser_type encountered %s' % parser_type)


def get_atlas_path(resource_path):
    return os.path.join(resource_path, 'atlases')


def clear_atlas_dir(directory):
    if(os.path.isdir(directory)):
        shutil.rmtree(directory)
    os.mkdir(directory)
