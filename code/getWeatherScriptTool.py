# getWeatherScriptTool.py
# Author: Phillip Pegelow
# Unity id: pdpegelo

"""This is an ArcMap script tool interface for running the 'getWeather.py'
module."""

import sys
import getWeather
import arcpy
import os


# Run the tool
arcpy.SetProgressor("default", "Progress")
arcpy.SetProgressorLabel("Starting tool...")
file = sys.argv[1]
startDate = getWeather.dateFormat(sys.argv[2])
endDate = getWeather.dateFormat(sys.argv[3])
arcpy.SetProgressorLabel("Obtaining FIPS Codes...")
fileWithFips = getWeather.addFips(file)
arcpy.SetProgressorLabel("Generating FIPS Codes List...")
listOfFips = getWeather.createFipsList(fileWithFips)
arcpy.SetProgressorLabel("Fetching Weather Data from NOAA API...")
withFips = getWeather.addSummaryData(
    fileWithFips,
    listOfFips,
    startDate,
    endDate)
arcpy.SetProgressorLabel("Adding fields...")
getWeather.dissolveStats(withFips, file)
arcpy.SetProgressorLabel("Finishing up...")


# Add scratch files to map.  They are useful
fips = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))),
    "data",
    "UScounties.shp")
withFips = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))),
    "data",
    "ShapeWithFips.shp")
fipsDissolved = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))),
    "data",
    "FipsDissolved.shp")
finalOutput = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))),
    "data",
    "WeatherData.shp")

# Initialize data variables
arcpy.env.workspace = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))),
    "data")
mapName = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))),
    "getWeather.mxd")

# Instantiate mapDocument, dataFrame, and Layer objects.
mxd = arcpy.mapping.MapDocument(mapName)
dfs = arcpy.mapping.ListDataFrames(mxd)
# get the first data frame
df = dfs[0]
addLayer = arcpy.mapping.Layer(os.path.basename(withFips))

# Add the new layer to the map
arcpy.mapping.AddLayer(df, addLayer)

# Save a copy of the map.
copyName = mapName[:-4] + "2.mxd"
mxd.saveACopy(copyName)

# Delete the mapDocument object to release the map.
del mxd
