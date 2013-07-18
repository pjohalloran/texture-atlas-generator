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

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from atlas.atlas_data import AtlasData
from util.utils import get_color
from util.utils import get_packer
from util.utils import get_parser
from math.math import next_power_of_two
from packing_algorithms.texture_packer import PackerError


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

    args = vars(arg_parser.parse_args())

    return {'parser': arg_parser, 'args': args}


def get_font_chars(char_file_path):
    chars_file = open(char_file_path)
    return chars_file.read()


def get_fonts_path(res_path):
    return os.path.join(res_path, 'fonts')


def create_fonts_dir(res_path):
    fonts_path = get_fonts_path(res_path)
    if not os.path.exists(fonts_path):
        os.mkdir(fonts_path)


def pack_fonts(font_filename, point_size, text, color, atlas_size):
    texture_packer = get_packer('maxrects', str(atlas_size), 'area')
    font = ImageFont.truetype(font_filename, point_size)

    image_dict = {}
    for character in text:
        size = font.getsize(character)
        name = '%s_%s_%s' % (os.path.basename(font_filename), str(point_size), character)
        image_dict[name] = Image.new('RGBA', size, color)
        draw = ImageDraw.Draw(image_dict[name])
        draw.text((0, 0), character, font=font)
        texture_packer.add_texture(image_dict[name].size[0], image_dict[name].size[1], name)

    # Pack the textures into an atlas as efficiently as possible.
    packResult = texture_packer.pack_textures(True, True)

    return (texture_packer, packResult, image_dict)


def create_imagefont(res_path, font_filename, point_size, text, color):
    done = False
    curr_size = 64
    texture_packer = None
    image_dict = None
    packResult = None

    # Retry until optimal font atlas size is found.
    while not done:
        try:
            result = pack_fonts(font_filename, point_size, text, color, curr_size)
            texture_packer = result[0]
            packResult = result[1]
            image_dict = result[2]
            done = True
        except PackerError:
            curr_size = next_power_of_two(curr_size)
            print "Failed, trying next power of two", curr_size

    borderSize = 1
    font_image_name = os.path.join(get_fonts_path(res_path), '%s_%s.%s' % (os.path.basename(font_filename).split('.')[0], str(point_size), 'tga'))
    atlas_data = AtlasData(name=font_image_name, width=packResult[0], height=packResult[1], color_mode='RGBA', file_type='tga', border=borderSize)
    for tex in texture_packer.texArr:
        atlas_data.add_texture(tex)

    parser = get_parser('xml')
    parser.parse(atlas_data)
    parser.save('%s.%s' % (font_image_name.split('.')[0], parser.get_file_ext()))

    atlas_image = Image.new('RGBA', (packResult[0], packResult[1]), color)

    index = 0
    for name in image_dict.keys():
        tex = texture_packer.get_texture(name)
        atlas_image.paste(image_dict[name], (tex.x, tex.y))
        index += 1

    atlas_image.save(os.path.join(get_fonts_path(res_path), font_image_name), 'tga')


def main():
    parser_dict = parse_args()

    create_fonts_dir(parser_dict['args']['res_path'])

    font_chars = get_font_chars(parser_dict['args']['char_file'])
    point_sizes_list = parser_dict['args']['point_sizes'].split(',')

    for size in point_sizes_list:
        print "Creating for ", size
        create_imagefont(parser_dict['args']['res_path'], parser_dict['args']['font_file'], int(size), font_chars, get_color(parser_dict['args']['bg_color']))


if __name__ == "__main__":
    main()
