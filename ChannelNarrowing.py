# The source code of the tool
import arcpy
import os


def main(historicBankfull, modernBankfull, reachBreaks, centerline, outputFolderLocation, outputName, isSegmented):
    """
    Source code of the tool
    :param historicBankfull: A polygon with the historic bankfull value
    :param modernBankfull: A polygon with the modern bankfull value
    :param reachBreaks: A series of lines that tell us when to break the thing
    :param centerline: The centerline of the modern bankfull polygon
    :param outputFolderLocation: Where the project folder should go
    :param outputName: What the output should be named
    :param isSegmented: Tells us if the technician has segmented the input beforehand
    :return:
    """
    arcpy.env.overwriteOutput = True
    isSegmented = parseArcBool(isSegmented)

    if not isSegmented and not reachBreaks:
        raise Exception("You did not provide a way for us to segment the inputs!")

    projectFolder = makeFolder(outputFolderLocation, "ChannelNarrowingProject")
    inputFolder = makeFolder(projectFolder, "01_Inputs")
    historicBankfull, modernBankfull, centerline, reachBreaks = copyInputs(inputFolder, historicBankfull, modernBankfull, centerline, reachBreaks)

    outputFolder, analysesFolder, historicBankfull, modernBankfull, centerline = writeOutputFolder(projectFolder, historicBankfull, modernBankfull, reachBreaks, centerline, isSegmented)

    assignArea(historicBankfull, "Hist_Area")
    assignArea(modernBankfull, "Crnt_Area")

    historicBankfullLayer = "historicBankful_lyr"
    modernBankfullLayer = "modernBankful_lyr"
    arcpy.MakeFeatureLayer_management(historicBankfull, historicBankfullLayer)
    arcpy.MakeFeatureLayer_management(modernBankfull, modernBankfullLayer)
    polygonOutputFile = os.path.join(analysesFolder, outputName + "_Polygon.shp")

    arcpy.SpatialJoin_analysis(modernBankfullLayer, historicBankfullLayer, polygonOutputFile, match_option="INTERSECT")




def writeOutputFolder(projectFolder, historicBankfull, modernBankfull, reachBreaks, centerline, isSegmented):
    """
    Writes the structure of the output folder and creates the intermediates
    :param projectFolder:
    :param historicBankfull:
    :param modernBankfull:
    :param reachBreaks:
    :param centerline:
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
        modernBankfull, historicBankfull = segmentBankfulls(historicBankfull, modernBankfull, reachBreaks, intermediateFolder)
        centerline = segmentCenterline(centerline, reachBreaks, intermediateFolder)

    arcpy.AddMessage("Making Analyses...")
    analysesFolder = makeFolder(outputFolder, findAvailableNum(outputFolder) + "_Analyses")
    return outputFolder, analysesFolder, historicBankfull, modernBankfull, centerline


def segmentCenterline(centerline, reachBreaks, intermediateFolder):
    """

    :param centerline:
    :param reachBreaks:
    :return:
    """
    centerlineFolder = makeFolder(intermediateFolder, findAvailableNum(intermediateFolder) + "_SegmentedCenterline")

    givenBankfullLayer = os.path.join(centerlineFolder, "old.lyr")
    arcpy.MakeFeatureLayer_management(centerline, givenBankfullLayer)

    segCenterline = os.path.join(centerlineFolder, "SegmentedCenterline.shp")
    segCenterlineNew = os.path.join(centerlineFolder, "CleanedSegmentedCenterline")
    tempCenterlineLayer = "temp_lyr"
    segCenterlineLayer = "segCenterline_lyr"
    centerlineLayer = "centerline_lyr"

    tempCenterline = os.path.join(centerlineFolder, "Temp.shp")
    arcpy.MakeFeatureLayer_management(centerline, tempCenterlineLayer)
    arcpy.Dissolve_management(tempCenterlineLayer, tempCenterline)

    arcpy.Delete_management(segCenterline)

    arcpy.FeatureToLine_management([reachBreaks, centerline], segCenterline)

    arcpy.MakeFeatureLayer_management(segCenterline, segCenterlineLayer)
    arcpy.MakeFeatureLayer_management(centerline, centerlineLayer)

    arcpy.SelectLayerByLocation_management(segCenterlineLayer, "WITHIN", givenBankfullLayer)
    arcpy.CopyFeatures_management(segCenterlineLayer, segCenterlineNew)

    return segCenterline


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
        if arcpy.Describe(reachBreak).shapeType == "Polygon":
            arcpy.FeatureToLine_management(reachBreak, reachBreakCopy)
        else:
            arcpy.Copy_management(reachBreak, reachBreakCopy)

    return historicBankfullCopy, modernBankfullCopy, centerlineCopy, reachBreakCopy


def segmentBankfulls(historicBankfull, modernBankfull, reachBreak, intermediateFolder):
    """
    Segments the inputs based on the reach breaks given to it
    :param historicBankfull: A polygon with the historic bankfull value
    :param modernBankfull: A polygon with the modern bankfull value
    :param reachBreak: A series of lines that tell us when to break the thing
    :param intermediateFolder: Path to the intermediates folder
    :return: The paths to the segmented modern and historic bankfull shape files, respectively
    :rtype: A tuple of strings with length 2
    """
    bufferedReachBreaksFolder = makeFolder(intermediateFolder, "01_ReachBreakBuffer")
    segHistoricBankfullFolder = makeFolder(intermediateFolder, "02_HistoricBankfullSegmented")
    segModernBankfullFolder = makeFolder(intermediateFolder, "03_ModernBankfullSegmented")

    bufferedReachBreaks = os.path.join(bufferedReachBreaksFolder, "Buffered_Reach_Breaks.shp")
    arcpy.Buffer_analysis(reachBreak, bufferedReachBreaks, "1 Foot")

    cleanedSegModernBankfull = segmentBankfull(modernBankfull, bufferedReachBreaks, segModernBankfullFolder, "ModernBankfull")
    cleanedSegHistoricBankfull = segmentBankfull(historicBankfull, bufferedReachBreaks, segHistoricBankfullFolder, "HistoricBankfull")

    return cleanedSegModernBankfull, cleanedSegHistoricBankfull


def segmentBankfull(givenBankfull, bufferedReachBreaks, outputLocation, outputName):
    """
    Segments the given bankfull and returns a path to it
    :param givenBankfull: What we want to segment
    :param bufferedReachBreaks: What we segment with
    :param outputLocation: Where we put the segmented bankfull
    :param outputName: What we'll name the output
    :return: Path to the segmented bankfull
    """
    givenBankfullLayer = os.path.join(outputLocation, "old.lyr")
    arcpy.MakeFeatureLayer_management(givenBankfull, givenBankfullLayer)

    segBankfull = os.path.join(outputLocation, outputName + ".shp")
    tempSegBankfull = os.path.join(outputLocation, "Temp.shp")
    tempSegBankfullLayer = "temp_lyr"
    cleanedSegBankfull = os.path.join(outputLocation, "Cleaned" + outputName + ".shp")

    arcpy.Delete_management(segBankfull)
    arcpy.Delete_management(cleanedSegBankfull)
    arcpy.Delete_management(tempSegBankfullLayer)

    segBankfullLayer = outputName + "_lyr"

    arcpy.FeatureToPolygon_management([givenBankfull, bufferedReachBreaks], segBankfull)

    # Cleans up any polygons made by the Feature To Polygon tool
    arcpy.MakeFeatureLayer_management(segBankfull, segBankfullLayer)
    arcpy.SelectLayerByLocation_management(segBankfullLayer, "WITHIN", givenBankfullLayer)
    arcpy.CopyFeatures_management(segBankfullLayer, tempSegBankfull)

    #Remove Buffered region
    arcpy.MakeFeatureLayer_management(tempSegBankfull, tempSegBankfullLayer)
    arcpy.SelectLayerByLocation_management(tempSegBankfullLayer, "WITHIN", bufferedReachBreaks, invert_spatial_relationship="INVERT")
    arcpy.CopyFeatures_management(tempSegBankfullLayer, cleanedSegBankfull)

    arcpy.Delete_management(tempSegBankfullLayer)

    return cleanedSegBankfull


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
