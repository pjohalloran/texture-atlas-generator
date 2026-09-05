#!/usr/bin/env python

# ###################################################
# @file AtlasGenerator.py
# @author PJ O Halloran (pjohalloran at gmail dot com)
#
# Parses all images in a directory and
# generates texture atlases and an xml dictionary
# describing the atlas.
#
# This script is provided for free under the MIT license:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# ###################################################

import os.path
import argparse
import logging
import sys
from typing import Any, Dict, List, Tuple

from PIL import Image
from PIL.Image import Image as ImageType

from atlas.atlas_data import AtlasData
from packing_algorithms.texture_packer import TexturePacker, retry_with_growing_bin_size
from util.utils import get_parser
from util.utils import get_packer
from util.utils import get_atlas_path
from util.utils import clear_atlas_dir
from util.utils import get_color

logger = logging.getLogger(__name__)


def pack_atlas(args: Dict[str, Any], dirPath: str, curr_size: int) -> Tuple[TexturePacker, Tuple[int, int, int], List[Tuple[str, ImageType]], bool]:
    """Open every image file directly inside dirPath and add it to a fresh
    texture packer sized for curr_size.

    Returns a (texture_packer, pack_result, images_list, had_errors) tuple,
    where images_list holds (filename, PIL.Image) pairs for the images that
    were successfully opened and packed, and had_errors is True if any
    image in dirPath failed to open.
    """
    texture_packer = get_packer(args['packing_algorithm'], curr_size, args['maxrects_heuristic'], args['allow_rotations'])
    childDirs = os.listdir(dirPath)

    imagesList = []
    had_errors = False

    # Open all images in the directory and add to the packer input data structure.
    for currPath in childDirs:
        file_path = os.path.join(dirPath, currPath)
        if (currPath.startswith(".") or os.path.isdir(file_path)):
            continue

        try:
            img = Image.open(file_path)
            texture_packer.add_texture(img.size[0], img.size[1], currPath)
            imagesList.append((currPath, img))
        except (IOError):
            logger.error("PIL failed to open file: %s", file_path)
            had_errors = True

    # Pack the textures into an atlas as efficiently as possible.
    packResult = texture_packer.pack_textures(True, True)

    return (texture_packer, packResult, imagesList, had_errors)


def create_atlas(texMode: str, dirPath: str, atlasPath: str, dirName: str, args: Dict[str, Any]) -> bool:
    """Pack every image in dirPath into a single atlas, retrying at the next
    power-of-two bin size each time the current size can't fit them all, then
    write the atlas image and its manifest (xml/json) to atlasPath.

    Returns False if any image in dirPath failed to open, True otherwise.
    """
    texture_packer, packResult, imagesList, had_errors = retry_with_growing_bin_size(
        lambda curr_size: pack_atlas(args, dirPath, curr_size),
        int(args['maxrects_bin_size']),
    )

    borderSize = 1
    atlas_data = AtlasData(name=dirName, width=packResult[0], height=packResult[1], color_mode=texMode, file_type=args['atlas_type'], border=borderSize)
    for tex in texture_packer.texArr:
        atlas_data.add_texture(tex)

    parser = get_parser(args['output_data_type'])
    parser.parse(atlas_data)
    parser.save('%s.%s' % (os.path.join(atlasPath, os.path.basename(dirPath)), parser.get_file_ext()))

    atlas_image = Image.new(texMode, (packResult[0], packResult[1]), get_color(args['bg_color']))

    for image_name, source_image in imagesList:
        tex = texture_packer.get_texture(image_name)
        if tex.flipped:
            source_image = source_image.transpose(Image.ROTATE_90)
        atlas_image.paste(source_image, (tex.x, tex.y))

    atlas_image.save(os.path.join(atlasPath, os.path.basename(dirPath)) + "." + args['atlas_type'], args['atlas_type'])
    if (args['verbose']):
        atlas_image.show()

    return not had_errors


def iterate_data_directory(texMode: str, atlasPath: str, resPath: str, args: Dict[str, Any]) -> bool:
    """Create one atlas per immediate subdirectory of resPath, treating each
    subdirectory's name as the atlas name and its contents as the images to
    pack into it. Images placed directly in resPath (not inside any
    subdirectory) are packed into one additional atlas, named after resPath
    itself.

    Returns False if any atlas had an image that failed to open, True
    otherwise.
    """
    all_ok = True
    has_root_images = False
    for currPath in os.listdir(resPath):
        if (currPath.startswith(".")):
            continue
        full_path = os.path.join(resPath, currPath)
        if (os.path.isdir(full_path)):
            if not create_atlas(texMode, full_path, atlasPath, currPath, args):
                all_ok = False
        else:
            has_root_images = True

    if has_root_images:
        if not create_atlas(texMode, resPath, atlasPath, os.path.basename(resPath), args):
            all_ok = False
    elif not any(os.path.isdir(os.path.join(resPath, p)) for p in os.listdir(resPath) if not p.startswith(".")):
        logger.warning("%s contains no images and no subdirectories - nothing to pack", resPath)

    return all_ok


def parse_args() -> Dict[str, Any]:
    arg_parser = argparse.ArgumentParser(description='Command line tool for creating texture atlases.')

    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-r', '--res-path', action='store', required=True, help='The location of the games resources.')
    arg_parser.add_argument('-t', '--atlas-type', action='store', required=False, default='tga', choices=('tga', 'png', 'jpg', 'jpeg'), help='The file type of the texture atlases')
    arg_parser.add_argument('-m', '--atlas-mode', action='store', required=False, default='RGBA', choices=('RGB', 'RGBA'), help='The bit mode of the texture atlases')
    arg_parser.add_argument('-o', '--output-data-type', action='store', required=False, default='xml', choices=('xml', 'json'), help='The file output type of the atlas dictionary')
    arg_parser.add_argument('-i', '--images-dir', action='store', required=False, default='textures', help='The directory inside the resource path to search for images to batch into texture atlases.')
    arg_parser.add_argument('-c', '--bg-color', action='store', required=False, default='128,128,128,255', help='The background color of the unused area in the texture atlas (e.g. 255,255,255,255).')
    arg_parser.add_argument('-a', '--packing-algorithm', action='store', required=False, default='maxrects', choices=('ratcliff', 'maxrects'), help='The packing algorithm to use.')
    arg_parser.add_argument('-e', '--maxrects-heuristic', action='store', required=False, default='area', choices=('shortside', 'longside', 'area', 'bottomleft', 'contactpoint'), help='The packing heuristic/rule to use if the maxrects algorithm is selected.')
    arg_parser.add_argument('-s', '--maxrects-bin-size', action='store', required=False, default='1024', help='The size of atlas when using the maxrects algorithm.')
    arg_parser.add_argument('-x', '--allow-rotations', action='store_true', help='Allow the maxrects packer to rotate textures 90 degrees to improve packing density. Has no effect on the ratcliff algorithm, which always considers rotation.')

    args = vars(arg_parser.parse_args())

    return {'parser': arg_parser, 'args': args}


def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser_dict = parse_args()

    if (not os.path.isdir(parser_dict['args']['res_path'])):
        logger.error("Not passed a valid directory")
        parser_dict['parser'].print_help()
        return 1

    textures_dir = os.path.join(parser_dict['args']['res_path'], parser_dict['args']['images_dir'])

    if (not os.path.isdir(textures_dir)):
        logger.error("%s does not contain a images or textures directory named %s", parser_dict['args']['res_path'], parser_dict['args']['images_dir'])
        parser_dict['parser'].print_help()
        return 1

    atlasesPath = get_atlas_path(parser_dict['args']['res_path'])
    clear_atlas_dir(atlasesPath)

    ok = iterate_data_directory(parser_dict['args']['atlas_mode'], atlasesPath, textures_dir, parser_dict['args'])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
