# getWeather.py
# Author: Phillip Pegelow
# Unity id: pdpegelo

"""This is a module that utilized NOAA's National Climatic Data Center REST
API to download, extract, calculate, and append four summary fields to
a shapefile."""

import arcpy
import sys
import urllib2
import os
import json
import time

arcpy.env.overwriteOutput = True

# Paths to Scratch Files
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


def addFips(infile):
    """Takes feature class as input and adds corresponding zip code attribute.
    Returns full path of new file."""
    arcpy.Intersect_analysis([infile, fips], withFips)
    return withFips


def createFipsList(withFips):
    """Takes point feature class with 'FIPS' attribute as input, and returns a
    string list of all unique FIPS codes"""
    fipsList = []
    with arcpy.da.SearchCursor(withFips, "FIPS") as cursor:
        for row in cursor:
            if row not in fipsList:
                fipsList.append(row)
    fipsList.sort()
    fipsStrList = [' '.join(item) for item in fipsList]
    return fipsStrList


def createLocStatement(fipsStrList):
    """Takes list of fips as args and returns a location statement that can be
    appended to an API request to obtain information from all areas all at
    once.  This is unreliable."""
    locationStatement = ""
    for i in fipsStrList:
        locationStatement = locationStatement + "locationid=FIPS:" + i + "&"
    return locationStatement


def addSummaryData(withFips, fippers, startDate, endDate):
    """This function takes the following four required arguments:

    withFips: a feature class with a FIPS code field titled, 'FIPS'.
    This can be created with the addFips() function.

    fippers:  a list of all of withFips's FIPS codes in string format.  This
    can be obtained with crateFipsList() function.

    startDate: the beginning date for which you wish to obtain average
    precipitation.  Formatted 'YYYY-MM-DD' (string)

    endDate:  the end date for which you wish to obtain average precipitation.
    Formatted 'YYYY-MM-DD' (string)

    The full path name of a new shapefile in which four new fields are added
    is returned. The four fields are:

    'AvgPrecip' is the average daily precipitation that falls from the
    specified date range. (measured in tenths of mm)

    'MaxTemp' is the maximum recorded temperature recorded within the
    specified date range. (measured in tenths of degrees Celcius)

    'MinTemp' is the minimum recorded temperature recorded within the
    specified date range. (measured in tenths of degrees Celcius)

    'AvgSnow' is the average daily snowfall that fell within the specified
    date range. (measured in mm)
    """

    prcpDict = {}
    tmaxDict = {}
    tminDict = {}
    snowDict = {}
    snwdDict = {}

    for fip in fippers:
        time.sleep(.2)  # NOAA API only allows 5 calls per second
        try:
            # GET data from NOAA REST API
            url = "http://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&locationid=FIPS:{0}&startdate={1}&enddate={2}&limit=1000".format(
                fip,
                startDate,
                endDate)
            req = urllib2.Request(url)
            req.add_header('token', 'anqKNDjrBCHVWjeOywqNhuVaEpkxoHdP')
            response = urllib2.urlopen(req)
            data = json.load(response)

            # CALCULATE data for all stations and dates in FIPS code boundary
            rainTotal = 0
            raincount = 0
            snowTotal = 0
            snowcount = 0
            tmaxList = []
            tminList = []
            for result in data["results"]:
                if result["datatype"] == "PRCP":
                    raincount += 1
                    rainTotal = rainTotal + int(result["value"])
                elif result["datatype"] == "TMAX":
                    tmaxList.append(int(result["value"]))
                elif result["datatype"] == "TMIN":
                    tminList.append(int(result["value"]))
                elif result["datatype"] == "SNOW":
                    snowcount += 1
                    snowTotal = snowTotal + int(result["value"])

            averageRain = float(rainTotal) / float(raincount)
            prcpDict[fip] = averageRain

            tmaxList = map(int, tmaxList)
            tmaxDict[fip] = max(tmaxList)

            tminList = map(int, tminList)
            tminDict[fip] = min(tminList)

            averageSnow = float(snowTotal) / float(snowcount)
            snowDict[fip] = averageSnow

        except:
            print "Failed to obtain data for {0}".format(fip)

    # Add data fields to shapefile
    arcpy.AddField_management(withFips, "AvgPrecip", "FLOAT")
    arcpy.AddField_management(withFips, "MaxTemp", "FLOAT")
    arcpy.AddField_management(withFips, "MinTemp", "FLOAT")
    arcpy.AddField_management(withFips, "AvgSnow", "FLOAT")
    fields = ["FIPS", "AvgPrecip", "MaxTemp", "MinTemp", "AvgSnow"]
    with arcpy.da.UpdateCursor(withFips, fields) as cursor:
        for row in cursor:
            if row[0] in prcpDict:
                row[1] = prcpDict[row[0]]
            if row[0] in tmaxDict:
                row[2] = tmaxDict[row[0]]
            if row[0] in tminDict:
                row[3] = tminDict[row[0]]
            if row[0] in snowDict:
                row[4] = snowDict[row[0]]
            cursor.updateRow(row)

    return withFips


def dissolveStats(fileWithFips, origFile):
    """Dissolves weather data fields from fips into the original feature
    classes they were requested for.  This is not necessary for point
    features, but it is necessary for polygon or line features."""
    fieldName = "FID_" + os.path.basename(origFile)[0:6]
    statsExpr = [["AvgPrecip", "MEAN"], ["MaxTemp", "MAX"],
                 ["MinTemp", "MIN"], ["AvgSnow", "MEAN"]]
    arcpy.Dissolve_management(
        fileWithFips,
        fipsDissolved,
        fieldName,
        statsExpr)

    # Join fields to original file
    arcpy.JoinField_management(
        origFile, "FID", fipsDissolved, fieldName, [
            "MEAN_AvgPr", "MAX_MaxTem", "MIN_MinTem", "MEAN_AvgSn"])


def dateFormat(date):
    """Reformats arcgis script tools date."""
    dateList = date.split("/")
    for x, i in enumerate(dateList):
        if len(i) == 1:
            dateList[x] = "0" + i
    year = dateList[2][0:4]
    month = dateList[0]
    day = dateList[1]
    return "{0}-{1}-{2}".format(year, month, day)
