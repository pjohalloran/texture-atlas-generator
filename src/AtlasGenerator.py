#!/usr/bin/env python

# ###################################################
# @file AtlasGenerator.py
# @author PJ O Halloran (pjohalloran at gmail dot com)
#
# Parses all images in a directory and
# generates texture atlases and an xml dictionary
# describing the atlas.
#
# Depends on the PIL image library to read in the images
# and create the atlases and standard python for
# creating the atlas xml dictionary file.
#
# Texture atlas packing algorithm is a python
# implementation of the C TexturePacker algorithm
# (c) 2009 by John W. Ratcliff.
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

from PIL import Image
import os.path
import shutil
import argparse
import xml.dom.minidom
from packing_algorithms.texture_packer_ratcliff import TexturePacker


# Directory where images are not baked into texture atlases during resource build.
gNoAtlasDir = "NoAtlas/"
# Location in resources where textures are grouped.
gImagesDir = "textures/"

gOutputAtlasXml = "AtlasInfo.xml"

gDoc = xml.dom.minidom.Document()
gRootElement = gDoc.createElement("Root")
gDoc.appendChild(gRootElement)

gTexturePacker = TexturePacker()


def create_atlas(texMode, dirPath, atlasPath, dirName, args):
    # 4 xml file to be read in at runtime which holds the texture coordinates, etc. in the atlas for each image stored in the atlas.
    print texMode, dirPath, atlasPath

    childDirs = os.listdir(dirPath)

    index = 0
    imgNameList = []
    imagesPathList = []
    imagesList = []

    # Open all images in the directory and add to the packer.
    for currPath in childDirs:
        #print "Doing ", currPath, os.path.isdir(currPath)
        imgElement = gDoc.createElement("image")
        imgElement.setAttribute("imagefile", currPath)

        if (currPath.startswith(".") or os.path.isdir(os.path.join(dirPath, currPath))):
            continue

        try:
            imgNameList.append(currPath)
            imagesPathList.append(dirPath + "/" + currPath)
            img = Image.open(imagesPathList[len(imagesPathList)-1])
            gTexturePacker.add_texture(img.size[0], img.size[1], currPath)
            imagesList.append([img, imgElement])
            index += 1
        except (IOError):
            print "ERROR: PIL failed to open file", dirPath + currPath

    # Pack the textures into an atlas as efficiently as possible.
    packResult = gTexturePacker.pack_textures(True, True)
    borderSize = 1

    atlasElement = gDoc.createElement("Atlas")
    atlasElement.setAttribute("name", ("%s.TGA" % (dirName)))
    atlasElement.setAttribute("width", str(packResult[0]))
    atlasElement.setAttribute("height", str(packResult[1]))
    atlasElement.setAttribute("mode", texMode)
    atlasElement.setAttribute("border", str(borderSize))
    atlasElement.setAttribute("type", args['atlas_type'])

    if (gTexturePacker.get_texture_count() != len(imagesPathList) or gTexturePacker.get_texture_count() != len(imagesList)):
        print "MakeAtlas(): ERROR - number of textures in Packer is different to number of images in dir", gTexturePacker.get_texture_count(), len(imagesPathList), len(imagesList)
        exit(1)

    atlasTest = Image.new(texMode, (packResult[0], packResult[1]), (128, 128, 128))

    index = 0
    for image in imagesList:
        img = image[0]
        imgElement = image[1]
        tex = gTexturePacker.get_texture_by_name(imgNameList[index])

        atlasTest.paste(img, (tex.x, tex.y))

        imgElement.setAttribute("x", str(tex.x))
        imgElement.setAttribute("y", str(tex.y))
        imgElement.setAttribute("width", str(tex.width))
        imgElement.setAttribute("height", str(tex.height))
        imgElement.setAttribute("flipped", str(tex.flipped))

        atlasElement.appendChild(imgElement)

        index += 1

    atlasTest.save(atlasPath + "/" + os.path.basename(dirPath) + "." + args['atlas_type'], args['atlas_type'])
    if (args['verbose']):
        atlasTest.show()

    gRootElement.appendChild(atlasElement)


def iterate_data_directory(texMode, atlasPath, resPath, args):
    print texMode, atlasPath, resPath

    childDirs = os.listdir(resPath)

    for currPath in childDirs:
        if (currPath.startswith(".")):
            continue
        if (os.path.isdir(os.path.join(resPath, currPath))):
            gTexturePacker.reset()
            create_atlas(texMode, resPath + "/" + currPath, atlasPath, currPath, args)


def parse_args():
    arg_parser = argparse.ArgumentParser(description='Command line tool for creating texture atlases.')

    arg_parser.add_argument('-v', '--verbose', action='store_true')
    arg_parser.add_argument('-r', '--res-path', action='store', required=True, help='The location of the games resources.')
    arg_parser.add_argument('-t', '--atlas-type', action='store', required=False, default='TGA', help='The file type of the texture atlases')
    arg_parser.add_argument('-m', '--atlas-mode', action='store', required=False, default='RGBA', help='The bit mode of the texture atlases (RGBA, RGB)')

    args = vars(arg_parser.parse_args())

    return {'parser': arg_parser, 'args': args}


def get_atlas_path(resource_path):
    return "%s/atlases/" % (resource_path)


def clear_atlas_dir(directory):
    if(os.path.isdir(directory)):
        shutil.rmtree(directory)
    os.mkdir(directory)


def main():
    global gImagesDir

    parser_dict = parse_args()

    if (not os.path.isdir(parser_dict['args']['res_path'])):
        print "Not passed a valid directory"
        parser_dict['parser'].print_help()
        return 1

    if (not os.path.isdir(parser_dict['args']['res_path'] + "/" + gImagesDir)):
        print parser_dict['args']['res_path'], "does not contain a images or textures directory named", gImagesDir
        parser_dict['parser'].print_help()
        return 1

    atlasesPath = get_atlas_path(parser_dict['args']['res_path'])
    clear_atlas_dir(atlasesPath)

    res = iterate_data_directory(parser_dict['args']['atlas_mode'], atlasesPath, parser_dict['args']['res_path'] + "/" + gImagesDir, parser_dict['args'])

    file_object = open(atlasesPath + "atlasDictionary.xml", "w")
    gDoc.writexml(file_object, indent="\n", addindent="    ")

    return res


if __name__ == "__main__":
    main()
