import arcpy
import ChannelNarrowing

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Channel Narrowing Tool"
        self.alias = "Channel Narrowing Tool"

        # List of tool classes associated with this toolbox
        self.tools = [ChannelNarrowingTool]


class ChannelNarrowingTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ChannelNarrowingTool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Historic Bankfull Polygon",
            name="historicBankfull",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Modern Bankfull Polygon",
            name="modernBankfull",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Select Output Location",
            name="outputFolder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Select Output Name",
            name="outputName",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, p, messages):
        """The source code of the tool."""
        reload(ChannelNarrowing)
        ChannelNarrowing.main(p[0].valueAsText,
                              p[1].valueAsText,
                              p[2].valueAsText)
        return
