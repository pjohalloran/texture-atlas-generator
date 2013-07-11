import os.path
import shutil

from data_parsers.json_parser import JsonParser
from data_parsers.xml_parser import XmlParser
from data_parsers.parser import ParserError
from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff
from packing_algorithms.maxrects.texture_packer_maxrects import TexturePackerMaxRects
from packing_algorithms.maxrects.texture_packer_maxrects import FreeRectChoiceHeuristicEnum


def get_parser(parser_type):
    if parser_type == 'xml':
        return XmlParser()
    elif parser_type == 'json':
        return JsonParser()
    else:
        raise ParserError('Unknown parser_type encountered %s' % parser_type)


def get_maxrects_heuristic(heuristic):
    if heuristic == 'shortside':
        return FreeRectChoiceHeuristicEnum.RectBestShortSideFit
    elif heuristic == 'longside':
        return FreeRectChoiceHeuristicEnum.RectBestLongSideFit
    elif heuristic == 'area':
        return FreeRectChoiceHeuristicEnum.RectBestAreaFit
    elif heuristic == 'bottomleft':
        return FreeRectChoiceHeuristicEnum.RectBottomLeftRule
    elif heuristic == 'contactpoint':
        return FreeRectChoiceHeuristicEnum.RectContactPointRule
    else:
        raise NotImplementedError('Unknown heuristic enum encountered')


def get_packer(algorithm_type, size=0, heuristic=""):
    if algorithm_type == 'ratcliff':
        return TexturePackerRatcliff()
    elif algorithm_type == 'maxrects':
        return TexturePackerMaxRects(get_maxrects_heuristic(heuristic), int(size), int(size))
    else:
        raise NotImplementedError('%s is unknown or not implemented yet.' % (algorithm_type))


def get_atlas_path(resource_path):
    return os.path.join(resource_path, 'atlases')


def clear_atlas_dir(directory):
    if(os.path.isdir(directory)):
        shutil.rmtree(directory)
    os.mkdir(directory)
