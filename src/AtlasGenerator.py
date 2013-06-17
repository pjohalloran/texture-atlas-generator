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

# Command line args and parser
gCommandArgs = None
gParser = None

gOutputAtlasXml = "AtlasInfo.xml"

gDoc = xml.dom.minidom.Document()
gRootElement = gDoc.createElement("Root")
gDoc.appendChild(gRootElement)

gTexturePacker = TexturePacker()


# ###################################################
#
# ###################################################
def MakeAtlas(texMode, dirPath, atlasPath, dirName):
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
            gTexturePacker.AddTexture(img.size[0], img.size[1], currPath)
            imagesList.append([img, imgElement])
            index += 1
        except (IOError):
            print "ERROR: PIL failed to open file", dirPath + currPath

    # Pack the textures into an atlas as efficiently as possible.
    packResult = gTexturePacker.PackTextures(True, True)
    borderSize = 1

    atlasElement = gDoc.createElement("Atlas")
    atlasElement.setAttribute("name", ("%s.TGA" % (dirName)))
    atlasElement.setAttribute("width", str(packResult[0]))
    atlasElement.setAttribute("height", str(packResult[1]))
    atlasElement.setAttribute("mode", texMode)
    atlasElement.setAttribute("border", str(borderSize))
    atlasElement.setAttribute("type", gCommandArgs['atlas_type'])

    #gTexturePacker.Print()
    if (gTexturePacker.GetNumberTextures() != len(imagesPathList) or gTexturePacker.GetNumberTextures() != len(imagesList)):
        print "MakeAtlas(): ERROR - number of textures in Packer is different to number of images in dir", gTexturePacker.GetNumberTextures(), len(imagesPathList), len(imagesList)
        exit(1)

    atlasTest = Image.new(texMode, (packResult[0], packResult[1]), (128, 128, 128))

    index = 0
    for tmp in imagesList:
        img = tmp[0]
        imgElement = tmp[1]
        tex = gTexturePacker.GetTextureByName(imgNameList[index])

        atlasTest.paste(img, (tex.GetX(), tex.GetY()))

        imgElement.setAttribute("x", str(tex.GetX()))
        imgElement.setAttribute("y", str(tex.GetY()))
        imgElement.setAttribute("width", str(tex.GetWidth()))
        imgElement.setAttribute("height", str(tex.GetHeight()))
        imgElement.setAttribute("flipped", str(tex.IsFlipped()))

        atlasElement.appendChild(imgElement)

        index += 1

#        #print imagesList
#        print imagesPathList
#
#        if (os.path.exists(resPath + "/" + "test1." + gCommandArgs['atlas_type'])):
#        print "removing file"
#        os.remove(resPath + "/" + "test1." + gCommandArgs['atlas_type'])

    atlasTest.save(atlasPath + "/" + os.path.basename(dirPath) + "." + gCommandArgs['atlas_type'], gCommandArgs['atlas_type'])
    if (gCommandArgs['verbose']):
        atlasTest.show()

    gRootElement.appendChild(atlasElement)


def GenerateAtlases(texMode, atlasPath, resPath):
    print texMode, atlasPath, resPath

    childDirs = os.listdir(resPath)

    for currPath in childDirs:
#        print "Doing ", currPath, os.path.isdir(currPath)
        if (currPath.startswith(".")):
            continue
        if (os.path.isdir(os.path.join(resPath, currPath))):
            gTexturePacker.Reset()
            MakeAtlas(texMode, resPath + "/" + currPath, atlasPath, currPath)


# ###################################################
#
# ###################################################
def ParseCommandLineArgs():
    global gParser
    global gCommandArgs

    gParser = argparse.ArgumentParser(description='GameFramework command line tool for baking game images into Texture Atlases.')

    gParser.add_argument('-v', '--verbose', action='store_true')
    gParser.add_argument('-r', '--res-path', action='store', required=True, help='The location of the games resources.')
    gParser.add_argument('-t', '--atlas-type', action='store', required=False, default='TGA', help='The file type of the texture atlases')
    gParser.add_argument('-m', '--atlas-mode', action='store', required=False, default='RGBA', help='The bit mode of the texture atlases (RGBA, RGB)')

    gCommandArgs = vars(gParser.parse_args())


# ###################################################
#
# ###################################################
def Main():
    global gParser
    global gCommandArgs
    global gImagesDir

    ParseCommandLineArgs()
    #print "len(gCommandArgs)=", len(gCommandArgs)
    #print "res_path = ", gCommandArgs['res_path']
    #print "atlas_size = ", gCommandArgs['atlas_size']
    #print "atlas_type = ", gCommandArgs['atlas_type']
    #print "atlas_mode = ", gCommandArgs['atlas_mode']

    if (not os.path.isdir(gCommandArgs['res_path'])):
        print "Not passed a valid directory"
        gParser.print_help()
        return (1)

    if (not os.path.isdir(gCommandArgs['res_path'] + "/" + gImagesDir)):
        print gCommandArgs['res_path'], "does not contain a images or textures directory named", gImagesDir
        gParser.print_help()
        return (1)

    atlasesPath = gCommandArgs['res_path'] + "/" + "atlases/"

    if(os.path.isdir(atlasesPath)):
        shutil.rmtree(atlasesPath)
    os.mkdir(atlasesPath)

    res = GenerateAtlases(gCommandArgs['atlas_mode'], atlasesPath, gCommandArgs['res_path'] + "/" + gImagesDir)

    file_object = open(atlasesPath + "atlasDictionary.xml", "w")
    gDoc.writexml(file_object, indent="\n", addindent="    ")

    #print "resPath=", resPath
    return (res)


# ###################################################
# Main entry point.
# ###################################################
res = Main()
exit(res)
