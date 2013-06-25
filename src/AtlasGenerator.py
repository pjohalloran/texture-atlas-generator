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
import shutil
import argparse

from PIL import Image

from packing_algorithms.texture_packer_ratcliff import TexturePacker
from data_parsers.xml_parser import XmlParser
from data_parsers.json_parser import JsonParser
from data_parsers.parser import ParserError
from atlas.atlas_data import AtlasData


def get_parser(parser_type):
    if parser_type == 'xml':
        return XmlParser()
    elif parser_type == 'json':
        return JsonParser()
    else:
        raise ParserError('Unknown parser_type encountered %s' % parser_type)


def create_atlas(texMode, dirPath, atlasPath, dirName, args):
    texture_packer = TexturePacker()
    texture_packer.reset()
    parser = get_parser(args['output_data_type'])
    childDirs = os.listdir(dirPath)

    index = 0
    imagesList = []

    # Open all images in the directory and add to the packer input data structure.
    for currPath in childDirs:
        file_path = os.path.join(dirPath, currPath)
        if (currPath.startswith(".") or os.path.isdir(file_path)):
            continue

        try:
            img = Image.open(file_path)
            texture_packer.add_texture(img.size[0], img.size[1], currPath)
            imagesList.append((currPath, img))
            index += 1
        except (IOError):
            print "ERROR: PIL failed to open file: ", file_path

    # Pack the textures into an atlas as efficiently as possible.
    packResult = texture_packer.pack_textures(True, True)

    borderSize = 1
    atlas_name = '%s.%s' % (dirName, args['atlas_type'])
    atlas_data = AtlasData(name=atlas_name, width=packResult[0], height=packResult[1], color_mode=texMode, file_type=args['atlas_type'], border=borderSize)
    for tex in texture_packer.texArr:
        atlas_data.add_texture(tex)

    parser.parse(atlas_data)
    parser.save('%s.%s' % (os.path.join(atlasPath, os.path.basename(dirPath)), parser.get_file_ext()))

    atlas_image = Image.new(texMode, (packResult[0], packResult[1]), (128, 128, 128))

    index = 0
    for image in imagesList:
        tex = texture_packer.get_texture_by_name(image[0])
        atlas_image.paste(image[1], (tex.x, tex.y))
        index += 1

    atlas_image.save(os.path.join(atlasPath, os.path.basename(dirPath)) + "." + args['atlas_type'], args['atlas_type'])
    if (args['verbose']):
        atlas_image.show()


def iterate_data_directory(texMode, atlasPath, resPath, args):
    childDirs = os.listdir(resPath)
    for currPath in childDirs:
        if (currPath.startswith(".")):
            continue
        if (os.path.isdir(os.path.join(resPath, currPath))):
            create_atlas(texMode, os.path.join(resPath, currPath), atlasPath, currPath, args)


def parse_args():
    arg_parser = argparse.ArgumentParser(description='Command line tool for creating texture atlases.')

    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-r', '--res-path', action='store', required=True, help='The location of the games resources.')
    arg_parser.add_argument('-t', '--atlas-type', action='store', required=False, default='tga', choices=('tga', 'png', 'jpg', 'jpeg'), help='The file type of the texture atlases')
    arg_parser.add_argument('-m', '--atlas-mode', action='store', required=False, default='RGBA', choices=('RGB', 'RGBA'), help='The bit mode of the texture atlases')
    arg_parser.add_argument('-o', '--output-data-type', action='store', required=False, default='xml', choices=('xml', 'json'), help='The file output type of the atlas dictionary')
    arg_parser.add_argument('-i', '--images-dir', action='store', required=False, default='textures', help='The directory inside the resource path to search for images to batch into texture atlases.')

    args = vars(arg_parser.parse_args())

    return {'parser': arg_parser, 'args': args}


def get_atlas_path(resource_path):
    return os.path.join(resource_path, 'atlases')


def clear_atlas_dir(directory):
    if(os.path.isdir(directory)):
        shutil.rmtree(directory)
    os.mkdir(directory)


def main():
    parser_dict = parse_args()

    if (not os.path.isdir(parser_dict['args']['res_path'])):
        print "Not passed a valid directory"
        parser_dict['parser'].print_help()
        return 1

    textures_dir = os.path.join(parser_dict['args']['res_path'], parser_dict['args']['images_dir'])

    if (not os.path.isdir(textures_dir)):
        print parser_dict['args']['res_path'], "does not contain a images or textures directory named", parser_dict['args']['images_dir']
        parser_dict['parser'].print_help()
        return 1

    atlasesPath = get_atlas_path(parser_dict['args']['res_path'])
    clear_atlas_dir(atlasesPath)

    res = iterate_data_directory(parser_dict['args']['atlas_mode'], atlasesPath, textures_dir, parser_dict['args'])

    return res


if __name__ == "__main__":
    main()
