# The source code of the tool
import arcpy
import os


def main(historicBankfull, modernBankfull, reachBreak, outputFolder, outputName, isSegmented):
    """
    Source code of the tool
    :param historicBankfull: A polygon with the historic bankfull value
    :param modernBankfull: A polygon with the modern bankfull value
    :param reachBreak: A series of lines that tell us when to break the thing
    :param outputFolder: Where the project folder should go
    :param outputName: What the output should be named
    :param isSegmented: Tells us if the technician has segmented the input beforehand
    :return:
    """
    isSegmented = parseArcBool(isSegmented)

    if not isSegmented and not reachBreak:
        raise Exception("You did not provide a way for us to segment the inputs!")

    outputFolder = makeFolder(outputFolder, "ChannelNarrowingProject")

    if not isSegmented:
        intermediaryFolder = makeFolder(outputFolder, "02_Intermediaries")
        historicBankfull, modernBankfull = segmentBankfull(historicBankfull, modernBankfull, reachBreak, intermediaryFolder)






def segmentBankfull(historicBankfull, modernBankfull, reachBreak, intermediaryFolder):
    """
    Segments the inputs based on the reach breaks given to it
    :param historicBankfull: A polygon with the historic bankfull value
    :param modernBankfull: A polygon with the modern bankfull value
    :param reachBreak: A series of lines that tell us when to break the thing
    :param intermediaryFolder: Where we put our intermediary output
    :return: None
    """
    segHistoricBankfullFolder = makeFolder(intermediaryFolder, "01_HistoricBankfullSegmented")
    segModernBankfullFolder = makeFolder(intermediaryFolder, "02_ModernBankfullSegmented")

    historicBankfullLayer = os.path.join(segHistoricBankfullFolder, "old.lyr")
    arcpy.MakeFeatureLayer_management(historicBankfull, historicBankfullLayer)
    modernBankfullLayer = os.path.join(segModernBankfullFolder, "old.lyr")
    arcpy.MakeFeatureLayer_management(modernBankfull, modernBankfullLayer)

    segHistoricBankfull = os.path.join(segHistoricBankfullFolder, "historicBankfull.shp")
    segModernBankfull = os.path.join(segModernBankfullFolder, "modernBankfull.shp")

    clippedSegHistoricBankfull = os.path.join(segHistoricBankfullFolder, "BetterHistoric.shp")
    clippedSegModernBankfull = os.path.join(segModernBankfullFolder, "BetterModern.shp")

    arcpy.Delete_management(segHistoricBankfull)
    arcpy.Delete_management(segModernBankfull)
    arcpy.Delete_management(clippedSegHistoricBankfull)
    arcpy.Delete_management(clippedSegModernBankfull)

    segHistoricBankfullLayer = os.path.join(segHistoricBankfullFolder, "historicBankfull_lyr")
    segModernBankfullLayer = os.path.join(segModernBankfullFolder, "modernBankfull_lyr")

    arcpy.FeatureToPolygon_management([historicBankfull, reachBreak], segHistoricBankfull)
    arcpy.MakeFeatureLayer_management(segHistoricBankfull, segHistoricBankfullLayer)
    arcpy.FeatureToPolygon_management([modernBankfull, reachBreak], segModernBankfull)
    arcpy.MakeFeatureLayer_management(segModernBankfull, segModernBankfullLayer)

    cleanedSegHistoricBankfull = os.path.join(segHistoricBankfullFolder, "BetterHistoric.shp")
    arcpy.SelectLayerByLocation_management(segHistoricBankfullLayer, "WITHIN", historicBankfullLayer)
    arcpy.CopyFeatures_management(segHistoricBankfullLayer, cleanedSegHistoricBankfull)

    cleanedSegModernBankfull = os.path.join(segModernBankfullFolder, "CleanedModernBankfull.shp")
    arcpy.SelectLayerByLocation_management(segModernBankfullLayer, "WITHIN", modernBankfullLayer)
    arcpy.CopyFeatures_management(segModernBankfullLayer, cleanedSegModernBankfull)

    return segHistoricBankfull, segModernBankfull

def makeFolder(pathToLocation, newFolderName):
    """
    Makes a folder and returns the path to it
    :param pathToLocation: Where we want to put the folder
    :param newFolderName: What the folder will be called
    :return: String
    """
    newFolder = os.path.join(pathToLocation, newFolderName)
    if not os.path.exists(newFolder):
        os.mkdir(newFolder)
    return newFolder


def parseArcBool(givenBool):
    """
    Resolves the text given as a boolean
    :param givenBool: The bool passed to the tool by the user
    :return:
    """
    if givenBool == 'false' or givenBool is None:
        return False
    else:
        return True