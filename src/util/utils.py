import os.path
import shutil
from typing import Tuple, Union

from data_parsers.json_parser import JsonParser
from data_parsers.parser import Parser, ParserError
from data_parsers.xml_parser import XmlParser
from packing_algorithms.maxrects.texture_packer_maxrects import FreeRectChoiceHeuristicEnum
from packing_algorithms.maxrects.texture_packer_maxrects import TexturePackerMaxRects
from packing_algorithms.ratcliff.texture_packer_ratcliff import TexturePackerRatcliff
from packing_algorithms.texture_packer import TexturePacker


def get_parser(parser_type: str) -> Parser:
    if parser_type == 'xml':
        return XmlParser()
    elif parser_type == 'json':
        return JsonParser()
    else:
        raise ParserError('Unknown parser_type encountered %s' % parser_type)


def get_maxrects_heuristic(heuristic: str) -> int:
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


def get_packer(algorithm_type: str, size: Union[int, str] = 0, heuristic: str = "", allow_rotations: bool = False) -> TexturePacker:
    if algorithm_type == 'ratcliff':
        packer = TexturePackerRatcliff()
    elif algorithm_type == 'maxrects':
        packer = TexturePackerMaxRects(get_maxrects_heuristic(heuristic), int(size), int(size))
    else:
        raise NotImplementedError('%s is unknown or not implemented yet.' % (algorithm_type))

    # Only affects maxrects - ratcliff always considers rotation as part of
    # its own algorithm, unrelated to this flag.
    packer.allow_rotations = allow_rotations
    return packer


def get_atlas_path(resource_path: str) -> str:
    return os.path.join(resource_path, 'atlases')


def get_color(color_text: str) -> Tuple[int, ...]:
    color_list = color_text.split(',')
    color_ints = list(map(int, color_list))
    return tuple(color_ints[:len(color_ints)])


def clear_atlas_dir(directory: str) -> None:
    if (os.path.isdir(directory)):
        shutil.rmtree(directory)
    os.mkdir(directory)
