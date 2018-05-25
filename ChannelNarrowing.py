# The source code of the tool
import arcpy
import os


def main(historicBankfull, modernBankfull, reachBreak, centerline, outputFolderLocation, outputName, isSegmented):
    """
    Source code of the tool
    :param historicBankfull: A polygon with the historic bankfull value
    :param modernBankfull: A polygon with the modern bankfull value
    :param reachBreak: A series of lines that tell us when to break the thing
    :param centerline: The centerline of the modern bankfull polygon
    :param outputFolderLocation: Where the project folder should go
    :param outputName: What the output should be named
    :param isSegmented: Tells us if the technician has segmented the input beforehand
    :return:
    """
    arcpy.env.overwriteOutput = True
    isSegmented = parseArcBool(isSegmented)


    if not isSegmented and not reachBreak:
        raise Exception("You did not provide a way for us to segment the inputs!")

    projectFolder = makeFolder(outputFolderLocation, "ChannelNarrowingProject")
    inputFolder = makeFolder(projectFolder, "01_Inputs")
    historicBankfull, modernBankfull, centerline, reachBreak = copyInputs(inputFolder, historicBankfull, modernBankfull, centerline, reachBreak)

    outputFolder, analysesFolder, historicBankfull, modernBankfull = writeOutputFolder(projectFolder, historicBankfull, modernBankfull, reachBreak, isSegmented)

    assignArea(historicBankfull, "Hist_Area")
    assignArea(modernBankfull, "Crnt_Area")

    historicBankfullLayer = "historicBankful_lyr"
    modernBankfullLayer = "modernBankful_lyr"
    arcpy.MakeFeatureLayer_management(historicBankfull, historicBankfullLayer)
    arcpy.MakeFeatureLayer_management(modernBankfull, modernBankfullLayer)
    outputFile = os.path.join(analysesFolder, "ChannelNarrowing.shp")

    arcpy.SpatialJoin_analysis(modernBankfullLayer, historicBankfullLayer, outputFile, match_option="WITHIN")


def writeOutputFolder(projectFolder, historicBankfull, modernBankfull, reachBreak, isSegmented):
    """

    :param projectFolder:
    :param historicBankfull:
    :param modernBankfull:
    :param isSegmented:
    :return:
    """
    j = 1
    outputFolder = os.path.join(projectFolder, "Output_" + str(j))
    while os.path.exists(outputFolder):
        j += 1
        outputFolder = os.path.join(projectFolder, "Output_" + str(j))
    os.mkdir(outputFolder)

    intermediateFolder = None
    if not isSegmented:
        intermediateFolder = makeFolder(outputFolder, "01_Intermediates")
        segHistoricBankfullFolder = makeFolder(intermediateFolder, "01_HistoricBankfullSegmented")
        segModernBankfullFolder = makeFolder(intermediateFolder, "02_ModernBankfullSegmented")
        modernBankfull, historicBankfull = segmentBankfull(historicBankfull, modernBankfull, reachBreak, segHistoricBankfullFolder, segModernBankfullFolder)

    arcpy.AddMessage("Making Analyses...")
    analysesFolder = makeFolder(outputFolder, findAvailableNum(outputFolder) + "_Analyses")
    return outputFolder, analysesFolder, historicBankfull, modernBankfull


def copyInputs(inputFolder, historicBankfull, modernBankfull, centerline, reachBreak):
    """
    Puts the inputs in the proper folder structure
    :param inputFolder: Where to put everything
    :param historicBankfull: A polygon with the historic bankfull value
    :param modernBankfull: A polygon with the modern bankfull value
    :param centerline: The centerline of the modern bankfull polygon
    :param reachBreak: A series of lines that tell us when to break the thing
    :return: A tuple with the paths to the copies of the inputs
    """
    historicBankfullFolder = makeFolder(inputFolder, "01_HistoricBankfullSegmented")
    historicBankfullCopy = os.path.join(historicBankfullFolder, os.path.basename(historicBankfull))
    arcpy.Copy_management(historicBankfull, historicBankfullCopy)

    modernBankfullFolder = makeFolder(inputFolder, "02_ModernBankfullSegmented")
    modernBankfullCopy = os.path.join(modernBankfullFolder, os.path.basename(modernBankfull))
    arcpy.Copy_management(modernBankfull, modernBankfullCopy)

    centerlineFolder = makeFolder(inputFolder, "03_Centerline")
    centerlineCopy = os.path.join(centerlineFolder, os.path.basename(centerline))
    arcpy.Copy_management(centerline, centerlineCopy)

    reachBreakCopy = None
    if reachBreak:
        reachBreakFolder = makeFolder(inputFolder, "04_ReachBreaks")
        reachBreakCopy = os.path.join(reachBreakFolder, os.path.basename(reachBreak))
        arcpy.Copy_management(reachBreak, reachBreakCopy)

    return historicBankfullCopy, modernBankfullCopy, centerlineCopy, reachBreakCopy


def segmentBankfull(historicBankfull, modernBankfull, reachBreak, segHistoricBankfullFolder, segModernBankfullFolder):
    """
    Segments the inputs based on the reach breaks given to it
    :param historicBankfull: A polygon with the historic bankfull value
    :param modernBankfull: A polygon with the modern bankfull value
    :param reachBreak: A series of lines that tell us when to break the thing
    :param segHistoricBankfullFolder: Where to put the historic bankfull value
    :param segModernBankfullFolder: Where to put the modern bankfull value
    :return: The paths to the segmented modern and historic bankfull shape files, respectively
    :rtype: A tuple of strings with length 2
    """

    historicBankfullLayer = os.path.join(segHistoricBankfullFolder, "old.lyr")
    arcpy.MakeFeatureLayer_management(historicBankfull, historicBankfullLayer)
    modernBankfullLayer = os.path.join(segModernBankfullFolder, "old.lyr")
    arcpy.MakeFeatureLayer_management(modernBankfull, modernBankfullLayer)

    segHistoricBankfull = os.path.join(segHistoricBankfullFolder, "HistoricBankfull.shp")
    segModernBankfull = os.path.join(segModernBankfullFolder, "ModernBankfull.shp")
    cleanedSegHistoricBankfull = os.path.join(segHistoricBankfullFolder, "CleanedHistoricBankfull.shp")
    cleanedSegModernBankfull = os.path.join(segModernBankfullFolder, "CleanedModernBankfull.shp")

    arcpy.Delete_management(segHistoricBankfull)
    arcpy.Delete_management(segModernBankfull)
    arcpy.Delete_management(cleanedSegHistoricBankfull)
    arcpy.Delete_management(cleanedSegModernBankfull)

    segHistoricBankfullLayer = "historicBankfull_lyr"
    segModernBankfullLayer = "modernBankfull_lyr"

    arcpy.FeatureToPolygon_management([historicBankfull, reachBreak], segHistoricBankfull)
    arcpy.MakeFeatureLayer_management(segHistoricBankfull, segHistoricBankfullLayer)
    arcpy.FeatureToPolygon_management([modernBankfull, reachBreak], segModernBankfull)
    arcpy.MakeFeatureLayer_management(segModernBankfull, segModernBankfullLayer)

    arcpy.SelectLayerByLocation_management(segHistoricBankfullLayer, "WITHIN", historicBankfullLayer)
    arcpy.CopyFeatures_management(segHistoricBankfullLayer, cleanedSegHistoricBankfull)

    arcpy.SelectLayerByLocation_management(segModernBankfullLayer, "WITHIN", modernBankfullLayer)
    arcpy.CopyFeatures_management(segModernBankfullLayer, cleanedSegModernBankfull)

    return cleanedSegModernBankfull, cleanedSegHistoricBankfull


def assignArea(featureClass, fieldName='Sq_Meters'):
    """
    Gives the feature class a field with the area
    :param featureClass: The path to the shapefile that we'll modify
    :param fieldName: What we'll name the field
    :return:
    """
    units = arcpy.Describe(featureClass).spatialReference.linearUnitName
    arcpy.AddField_management(featureClass, fieldName, "DOUBLE")
    with arcpy.da.UpdateCursor(featureClass, ['SHAPE@AREA', fieldName]) as cursor:
        for row in cursor:
            row[1] = getMeters(row[0], units)
            cursor.updateRow(row)


def getMeters(area, units):
    if units.lower() == "foot":
        return area * 0.3048
    elif units.lower() == "meter":
        return area
    else:
        raise Exception("Unit type \"" + units + "\" is not supported by the converter")


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


def findAvailableNum(folderRoot):
    """
    Tells us the next number for a folder in the directory given
    :param folderRoot: Where we want to look for a number
    :return: A string, containing a number
    """
    takenNums = [fileName[0:2] for fileName in os.listdir(folderRoot)]
    POSSIBLENUMS = range(1, 100)
    for i in POSSIBLENUMS:
        stringVersion = str(i)
        if i < 10:
            stringVersion = '0' + stringVersion
        if stringVersion not in takenNums:
            return stringVersion
    arcpy.AddWarning("There were too many files at " + folderRoot + " to have another folder that fits our naming convention")
    return "100"
