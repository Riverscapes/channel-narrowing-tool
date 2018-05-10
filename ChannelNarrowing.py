# The source code of the tool
import arcpy


def main(streamNetwork, outputFolder, outputName):
    """
    Source code of the tool
    :param streamNetwork:
    :param outputFolder:
    :param outputName:
    :return:
    """
    arcpy.AddMessage(outputName)
    arcpy.AddMessage(streamNetwork)
    arcpy.AddMessage(outputFolder)
