#!/usr/bin/env python

# ###################################################
# @file ImageFontGenerator.py
# @author PJ O Halloran (pjohalloran at gmail dot com)
#
# Generates image fonts.
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

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from atlas.atlas_data import AtlasData
from util.utils import get_color
from util.utils import get_packer
from util.utils import get_parser
from geom.geom import next_power_of_two
from packing_algorithms.texture_packer import PackerError

logger = logging.getLogger(__name__)

# Upper bound on the retry-at-a-bigger-size loop in create_imagefont(); see
# the matching constant in AtlasGenerator.py for why a cap is needed.
MAX_ATLAS_SIZE = 16384


def parse_args():
    arg_parser = argparse.ArgumentParser(description='Command line tool for creating image fonts.')

    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-r', '--res-path', action='store', required=True, help='The location of the games resources.')
    arg_parser.add_argument('-i', '--char-file', action='store', required=True, help='The file containing the chars to generate in the image font')
    arg_parser.add_argument('-f', '--font-file', action='store', required=True, help='The truetype font to use to generate the image fonts')
    arg_parser.add_argument('-s', '--point-sizes', action='store', required=True, help='Comma delimited list of font point sizes to generate e.g \'10\' or \'10,12,18,32\'')
    arg_parser.add_argument('-t', '--atlas-type', action='store', required=False, default='tga', choices=('tga', 'png', 'jpg', 'jpeg'), help='The file type of the image font')
    arg_parser.add_argument('-o', '--output-data-type', action='store', required=False, default='xml', choices=('xml', 'json'), help='The file output type of the image font chars data dictionary')
    arg_parser.add_argument('-c', '--bg-color', action='store', required=False, default='255,255,255,0', help='The background color of the unused area in the texture atlas (e.g. 255,255,255,255).')
    arg_parser.add_argument('-a', '--packing-algorithm', action='store', required=False, default='maxrects', choices=('ratcliff', 'maxrects'), help='The packing algorithm to use to pack the font chars.')
    arg_parser.add_argument('-x', '--allow-rotations', action='store_true', help='Allow the maxrects packer to rotate glyphs 90 degrees to improve packing density. Has no effect on the ratcliff algorithm, which always considers rotation.')

    args = vars(arg_parser.parse_args())

    return {'parser': arg_parser, 'args': args}


def get_font_chars(char_file_path):
    with open(char_file_path) as chars_file:
        return chars_file.read()


def get_fonts_path(res_path):
    return os.path.join(res_path, 'fonts')


def create_fonts_dir(res_path):
    fonts_path = get_fonts_path(res_path)
    if not os.path.exists(fonts_path):
        os.mkdir(fonts_path)


def pack_fonts(font_filename, point_size, text, color, atlas_size, allow_rotations=False):
    """Render every character in text at point_size using font_filename onto
    its own RGBA image and pack them into a texture_packer sized for
    atlas_size.

    Returns a (texture_packer, pack_result, image_dict) tuple, where
    image_dict maps each generated glyph name to its rendered PIL.Image.
    """
    texture_packer = get_packer('maxrects', str(atlas_size), 'area', allow_rotations)
    font = ImageFont.truetype(font_filename, point_size)

    image_dict = {}
    for character in text:
        bbox = font.getbbox(character)
        size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
        name = '%s_%s_%s' % (os.path.basename(font_filename), str(point_size), character)
        image_dict[name] = Image.new('RGBA', size, color)
        draw = ImageDraw.Draw(image_dict[name])
        draw.text((0, 0), character, font=font)
        texture_packer.add_texture(image_dict[name].size[0], image_dict[name].size[1], name)

    # Pack the textures into an atlas as efficiently as possible.
    packResult = texture_packer.pack_textures(True, True)

    return (texture_packer, packResult, image_dict)


def create_imagefont(res_path, font_filename, point_size, text, color, atlas_type, output_data_type, allow_rotations=False):
    """Render every character in text at point_size, pack the glyphs into a
    single image font atlas (retrying at the next power-of-two bin size as
    needed), then write the atlas image and its manifest under
    res_path/fonts.
    """
    done = False
    curr_size = 64
    texture_packer = None
    image_dict = None
    packResult = None

    # Retry until optimal font atlas size is found.
    while not done:
        try:
            result = pack_fonts(font_filename, point_size, text, color, curr_size, allow_rotations)
            texture_packer = result[0]
            packResult = result[1]
            image_dict = result[2]
            done = True
        except PackerError:
            if curr_size >= MAX_ATLAS_SIZE:
                raise
            curr_size = next_power_of_two(curr_size)
            logger.info("Failed, trying next power of two: %s", curr_size)

    borderSize = 1
    font_image_name = os.path.join(get_fonts_path(res_path), '%s_%s.%s' % (os.path.basename(font_filename).split('.')[0], str(point_size), atlas_type))
    atlas_data = AtlasData(name=font_image_name, width=packResult[0], height=packResult[1], color_mode='RGBA', file_type=atlas_type, border=borderSize)
    for tex in texture_packer.texArr:
        atlas_data.add_texture(tex)

    parser = get_parser(output_data_type)
    parser.parse(atlas_data)
    parser.save('%s.%s' % (font_image_name.split('.')[0], parser.get_file_ext()))

    atlas_image = Image.new('RGBA', (packResult[0], packResult[1]), color)

    for name, glyph_image in image_dict.items():
        tex = texture_packer.get_texture(name)
        if tex.flipped:
            glyph_image = glyph_image.transpose(Image.ROTATE_90)
        atlas_image.paste(glyph_image, (tex.x, tex.y))

    atlas_image.save(font_image_name, atlas_type)


def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    parser_dict = parse_args()

    create_fonts_dir(parser_dict['args']['res_path'])

    font_chars = get_font_chars(parser_dict['args']['char_file'])
    point_sizes_list = parser_dict['args']['point_sizes'].split(',')

    for size in point_sizes_list:
        logger.info("Creating for %s", size)
        create_imagefont(parser_dict['args']['res_path'], parser_dict['args']['font_file'], int(size), font_chars, get_color(parser_dict['args']['bg_color']), parser_dict['args']['atlas_type'], parser_dict['args']['output_data_type'], parser_dict['args']['allow_rotations'])

    return 0


if __name__ == "__main__":
    sys.exit(main())
