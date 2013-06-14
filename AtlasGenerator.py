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


# ###################################################
#
# ###################################################
def IsPowerOfTwo(number=0):
    return ((number & (number - 1)) == 0) and number != 0


# ###################################################
#
# ###################################################
class Rect:
    def __init__(self, x1, y1, x2, y2):
        self.mX1 = x1
        self.mY1 = y1
        self.mX2 = x2
        self.mY2 = y2

    def Intersects(self, r):
        if (self.mX2 < r.mX1 or self.mX1 > r.mX2 or self.mY2 < r.mY1 or self.mY1 > r.mY2):
            return (False)
        return (True)

    def GetX1(self):
        return (self.mX1)

    def GetY1(self):
        return (self.mY1)

    def GetX2(self):
        return (self.mX2)

    def GetY2(self):
        return (self.mY2)

    def SetX1(self, x1):
        self.mX1 = x1

    def SetY1(self, y1):
        self.mY1 = y1

    def SetX2(self, x2):
        self.mX2 = x2

    def SetY2(self, y2):
        self.mY2 = y2

    def GetWidth(self):
        return (self.mX2 - self.mX1)

    def GetHeight(self):
        return (self.mY2 - self.mY1)

    def GetArea(self):
        return (self.GetWidth()*self.GetHeight())

    def Print(self):
        print "Rect = (x1=", self.mX1, "y1=", self.mY1, "x2=", self.mX2, "y2=", self.mY2, "width=", self.GetWidth(), "height=", self.GetHeight(), ")"


class Texture:
    def __init__(self, width, height, name=""):
        self.mWidth = width
        self.mHeight = height
        self.mX = 0
        self.mY = 0
        self.mArea = width * height
        self.mFlipped = False
        self.mPlaced = False
        self.mLongestEdge = width if width > height else height
        self.mName = name

    def Place(self, x, y, flipped=False):
        self.mX = x
        self.mY = y
        self.mFlipped = flipped
        self.mPlaced = True
        print "Placing ", self.mName, "at ", self.mX, self.mY

    def GetX(self):
        return (self.mX)

    def SetX(self, x):
        self.mX = x

    def GetY(self):
        return (self.mY)

    def SetY(self, y):
        self.mY = y

    def GetArea(self):
        return (self.mArea)

    def GetWidth(self):
        return (self.mWidth)

    def GetHeight(self):
        return (self.mHeight)

    def SetWidth(self, width):
        self.mWidth = width

    def SetHeight(self, height):
        self.mHeight = height

    def IsPlaced(self):
        return (self.mPlaced)

    def IsFlipped(self):
        return (self.mFlipped)

    def SetFlipped(self, flipped):
        self.mFlipped = flipped

    def FlipDimensions(self):
        if(self.mFlipped):
            tmp = self.mWidth
            self.mWidth = self.mHeight
            self.mHeight = tmp

    def GetRect(self):
        return (Rect(self.mX, self.mY, self.mX + self.mWidth, self.mY + self.mHeight))

    def GetLongestEdge(self):
        return (self.mLongestEdge)

    def GetName(self):
        return (self.mName)

    def SetName(self, name):
        self.mName = name

    def Print(self):
        print "Texture = (", self.GetRect().Print(), "area=", self.mArea, "flipped=", self.mFlipped, "placed=", self.mPlaced, "longestEdge=", self.mLongestEdge, "name=", self.mName, ")"


class Node:
    def __init__(self, x, y, width, height):
        self.mX = x
        self.mY = y
        self.mWidth = width
        self.mHeight = height

    def Fits(self, width, height):
        # 0 = bool, 1 = edgeCount
        resultList = []

        result = False
        edgeCount = 0

        if (width == self.mWidth or height == self.mHeight or width == self.mHeight or height == self.mWidth):
            if (width == self.mWidth):
                edgeCount += 1
            if (height == self.mHeight):
                edgeCount += 1
            elif (width == self.mHeight):
                edgeCount += 1
                if (height == self.mWidth):
                    edgeCount += 1
            elif (height == self.mWidth):
                edgeCount += 1
            elif (height == self.mHeight):
                edgeCount += 1

        if (width <= self.mWidth and height <= self.mHeight):
            result = True
        elif (height <= self.mWidth and width <= self.mHeight):
            result = True

        resultList.append(result)
        resultList.append(edgeCount)

        return (resultList)

    def GetRect(self):
        return (Rect(self.mX, self.mY, self.mX + self.mWidth, self.mY + self.mHeight))

    def GetX(self):
        return (self.mX)

    def GetY(self):
        return (self.mY)

    def SetX(self, x):
        self.mX = x

    def SetY(self, y):
        self.mY = y

    def SetWidth(self, width):
        self.mWidth = width

    def SetHeight(self, height):
        self.mHeight = height

    def Validate(self, node):
        r1 = self.GetRect()
        r2 = node.GetRect()
        return (r1 != r2)

    def Merge(self, node):
        ret = False
        r1 = self.GetRect()
        r2 = node.GetRect()

        r1.SetX2(r1.GetX2() + 1)
        r1.SetY2(r1.GetY2() + 1)
        r2.SetX2(r2.GetX2() + 1)
        r2.SetY2(r2.GetY2() + 1)

        if (r1.GetX1() == r2.GetX1() and r1.GetX2() == r2.GetX2() and r1.GetY1() == r2.GetY2()):
            self.mY = node.GetY()
            self.mHeight += node.GetRect().GetHeight()
            ret = True
        elif (r1.GetX1() == r2.GetX1() and r1.GetX2() == r2.GetX2() and r1.GetY2() == r2.GetY1()):
            self.mHeight += node.GetRect().GetHeight()
            ret = True
        elif (r1.GetY1() == r2.GetY1() and r1.GetY2() == r2.GetY1() and r1.GetX1() == r2.GetX2()):
            self.mX = node.GetX()
            self.mWidth += node.GetRect().GetWidth()
            ret = True
        elif (r1.GetY1() == r2.GetY1() and r1.GetY2() == r2.GetY1() and r1.GetX2() == r2.GetX1()):
            self.mWidth += node.GetRect().GetWidth()
            ret = True

        return ret

    def Print(self):
        print "Node = (x=", self.mX, "y=", self.mY, "width=", self.mWidth, "height=", self.mHeight, ")"


class TexturePacker:
    def __init__(self):
        self.Reset()

    def Print(self):
        print "List of textures:"
        for tex in self.mTextureArr:
            tex.Print()
        for node in self.mFreeArr:
            node.Print()
        print "Area = ", self.mTotalArea, "longest edge = ", self.mLongestEdge

    def Reset(self):
        self.mTextureArr = []
        self.mFreeArr = []
        self.mLongestEdge = 0
        self.mTotalArea = 0

    def GetNumberTextures(self):
        return (len(self.mTextureArr))

    def AddTexture(self, width, height, name=""):
        self.mTextureArr.append(Texture(width, height, name))
        self.mLongestEdge = width if (width > self.mLongestEdge) else self.mLongestEdge
        self.mLongestEdge = height if (height > self.mLongestEdge) else self.mLongestEdge
        self.mTotalArea += width * height

    def AddNode(self, x, y, width, height):
        self.mFreeArr.append(Node(x, y, width, height))

    def GetNextPowerOfTwo(self, num):
        p = 1
        while (p < num):
            p *= 2
        return (p)

    def GetTextureByName(self, name=""):
        if (len(name) == 0):
            return (None)

        index = 0
        tex = None
        for t in self.mTextureArr:
            if (t.GetName() == name):
                tex = t
                if(tex.IsFlipped()):
                    tex.FlipDimensions()
                return (tex)
            index += 1

        return (tex)

    def GetTexture(self, index):
        if(index < 0 or index >= len(self.mTextureArr)):
            return None

        tex = self.mTextureArr[index]
        if(tex.IsFlipped()):
            tex.FlipDimensions()
            return (True)

        return (False)

    def MergeNodes(self):
        for f in self.mFreeArr:
            fIdx = 0
            for s in self.mFreeArr:
                if (f != s):
                    if (f.Merge(s)):
                        self.mFreeArr[fIdx] = f
                        return (True)
            fIdx += 1

        return (False)

    def Validate(self):
        for f in self.mFreeArr:
            for c in self.mFreeArr:
                if (f != c):
                    f.Validate(c)

    def PackTextures(self, forcePowerOfTwo, onePixelBorder):
        # 0 = width
        # 1 = height
        # 3 = returnValue
        returnList = []

        if (onePixelBorder):
            i = 0
            for t in self.mTextureArr:
                t.SetWidth(t.GetWidth() + 2)
                t.SetHeight(t.GetHeight() + 2)
                self.mTextureArr[i] = t
                i += 1
            self.mLongestEdge += 2

        if (forcePowerOfTwo):
            self.mLongestEdge = self.GetNextPowerOfTwo(self.mLongestEdge)

        width = self.mLongestEdge
        count = self.mTotalArea / (self.mLongestEdge * self.mLongestEdge)
        height = (count + 2) * self.mLongestEdge

        self.AddNode(0, 0, width, height)

        # We must place each texture
        loopI = 0
        while (loopI < len(self.mTextureArr)):
            index = 0
            longestEdge = 0
            mostArea = 0

            # We first search for the texture with the longest edge, placing it first.
            # And the most area...
            j = 0
            for tmpTex in self.mTextureArr:
                #print "Checking texture ", tmpTex.GetName()
                if (not tmpTex.IsPlaced()):
                    if (tmpTex.GetLongestEdge() > longestEdge):
                        mostArea = tmpTex.GetArea()
                        longestEdge = tmpTex.GetLongestEdge()
                        index = j
                    elif (tmpTex.GetLongestEdge() == longestEdge):
                        if (tmpTex.GetArea() > mostArea):
                            mostArea = tmpTex.GetArea()
                            index = j
                j += 1

            # For the texture with the longest edge we place it according to this criteria.
            #   (1) If it is a perfect match, we always accept it as it causes the least amount of fragmentation.
            #   (2) A match of one edge with the minimum area left over after the split.
            #   (3) No edges match, so look for the node which leaves the least amount of area left over after the split.
            tex = self.mTextureArr[index]
            #print "Going to try and place ", tex.GetName()

            leastY = 0x7FFFFFFF
            leastX = 0x7FFFFFFF

            nodeIndex = 0
            idx = 0
            previousBestFitNodeIdx = 0
            bestFitNode = Node(0, 0, 0, 0)
            previousNodeIdx = 0
            edgeCount = 0

            # Walk the singly linked list of free nodes
            # see if it will fit into any currently free space
            for currNode in self.mFreeArr:
                resultFitsArr = currNode.Fits(tex.GetRect().GetWidth(), tex.GetRect().GetHeight())
                ec = resultFitsArr[1]

                # see if the texture will fit into this slot, and if so how many edges does it share.
                if (resultFitsArr[0] is True):
                    if (ec == 2):
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec
                        break

                    if (currNode.GetY() < leastY):
                        leastY = currNode.GetY()
                        leastX = currNode.GetX()
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec
                    elif (currNode.GetY() == leastY and currNode.GetX() < leastX):
                        leastX = currNode.GetX()
                        previousBestFitNodeIdx = previousNodeIdx
                        bestFitNode = currNode
                        nodeIndex = idx
                        edgeCount = ec

                previousNodeIdx = idx
                idx += 1

            # we should always find a fit location!
            if(bestFitNode.GetX() == 0 and bestFitNode.GetY() == 0 and bestFitNode.GetRect().GetWidth() == 0 and bestFitNode.GetRect().GetHeight() == 0):
                print "TexturePacker::PackTextures() BestFit node not found!!"
                exit(1)

            self.Validate()

            if (edgeCount == 0):
                if (tex.GetLongestEdge() <= bestFitNode.GetRect().GetWidth()):
                    if (tex.GetHeight() > tex.GetWidth()):
                        tex.FlipDimensions()
                        tex.SetFlipped(True)

                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), tex.IsFlipped())

                    self.AddNode(bestFitNode.GetX(), bestFitNode.GetY() + tex.GetHeight(), bestFitNode.GetRect().GetWidth(), bestFitNode.GetRect().GetHeight() - tex.GetHeight())

                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetWidth())
                    bestFitNode.SetWidth(bestFitNode.GetRect().GetWidth() - tex.GetWidth())
                    bestFitNode.SetHeight(tex.GetHeight())
                    self.Validate()
                else:
                    if (tex.GetLongestEdge() <= bestFitNode.GetHeight()):
                        print("TexturePacker::PackTexture() ERROR - Current textures longest edge is less than the BestFitNodes Height!!!")
                        exit(1)

                    if (tex.GetHeight() < tex.GetWidth()):
                        tex.FlipDimensions()
                        tex.SetFlipped(True)

                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), tex.IsFlipped())
                    self.AddNode(bestFitNode.GetX(), bestFitNode.GetY() + tex.GetHeight(), bestFitNode.GetRect().GetWidth(), bestFitNode.GetRect().GetHeight() - tex.GetHeight())
                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetWidth())
                    bestFitNode.SetWidth(bestFitNode.GetWidth() - tex.GetWidth())
                    bestFitNode.SetHeight(tex.GetHeight())
                    self.Validate()

            elif(edgeCount == 1):
                if (tex.GetWidth() == bestFitNode.GetRect().GetWidth()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), False)
                    bestFitNode.SetY(bestFitNode.GetY() + tex.GetHeight())
                    bestFitNode.SetHeight(bestFitNode.GetRect().GetHeight() - tex.GetHeight())
                    self.Validate()
                elif (tex.mHeight == bestFitNode.GetRect().GetHeight()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), False)
                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetWidth())
                    bestFitNode.SetWidth(bestFitNode.GetRect().GetWidth() - tex.GetWidth())
                    self.Validate()
                elif (tex.mWidth == bestFitNode.GetRect().GetHeight()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), True)
                    bestFitNode.SetX(bestFitNode.GetX() + tex.GetHeight())
                    bestFitNode.SetWidth(bestFitNode.GetRect().GetWidth() - tex.GetHeight())
                    self.Validate()
                elif (tex.mHeight == bestFitNode.GetRect().GetWidth()):
                    tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), True)
                    bestFitNode.SetY(bestFitNode.GetY() + tex.GetWidth())
                    bestFitNode.SetHeight(bestFitNode.GetHeight() - tex.GetWidth())
                    self.Validate()

            elif(edgeCount == 2):
                flipped = tex.GetWidth() != bestFitNode.GetRect().GetWidth() or tex.GetHeight() != bestFitNode.GetRect().GetHeight()
                tex.Place(bestFitNode.GetX(), bestFitNode.GetY(), flipped)
                if (previousBestFitNodeIdx >= 0):
                    previousBestFitNodeIdx = index
                self.Validate()

            # Save latest version of texture and Node back into lists since python is pass by value
            self.mFreeArr[nodeIndex] = bestFitNode
            self.mTextureArr[index] = tex

            loopI += 1

        while (self.MergeNodes()):
            print "Merging nodes"

        index = 0
        height = 0
        for t in self.mTextureArr:
            if (onePixelBorder):
                t.SetWidth(t.GetWidth() - 2)
                t.SetHeight(t.GetHeight() - 2)
                t.SetX(t.GetX() + 1)
                t.SetY(t.GetY() + 1)
                self.mTextureArr[index] = t

            y = 0
            if (t.IsFlipped()):
                y = t.GetY() + t.GetWidth()
            else:
                y = t.GetY() + t.GetHeight()

            if (y > height):
                height = y

            index += 1

        if (forcePowerOfTwo):
            height = self.GetNextPowerOfTwo(height)

        returnList.append(width)
        returnList.append(height)
        returnList.append((width * height) - self.mTotalArea)
        return (returnList)

# ###################################################
# Globals
# ###################################################

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
    atlasElement.setAttribute("name", dirName)
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
