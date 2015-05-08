# getWeatherTK.pyw
# Author: Phillip Pegelow
# Unity id: pdpegelo

"""This creates a GUI interface for the getWeather.py module.
When run, you will be prompted for a shapefile location, a start date,
and an end date.  When successful, the shapefilefile that you used, will have
four new weather-related fields added: Average Precipitation, Max Temperature,
Min Temperature, and Average Snowfall.  These are calculated from the date
range specified."""


import sys
import getWeather
import arcpy
from Tkinter import *
import tkFileDialog
import os


class App:

    def __init__(self, master):
        self.master = master

        # call start to initialize to create the UI elemets
        self.start()

    def start(self):
        self.master.title("NOAA Weather Data")

        # Create a label
        # create a variable with text
        label01 = "Choose Shapefile for which to add Weather Data"
        # put "label01" in "self.master" which is the window/frame
        # then, put in the first row (row=0) and in the 2nd column (column=1),
        # align it to "West"/"W"
        Label(self.master, text=label01).grid(row=0, column=0, sticky=W)

        # Create a textbox
        self.filelocation = Entry(self.master)
        self.filelocation["width"] = 30
        self.filelocation.focus_set()
        self.filelocation.grid(row=1, column=0)

        # Second textbox
        self.startDate = Entry(self.master)
        self.startDate["width"] = 30
        self.startDate.focus_set()
        self.startDate.grid(row=2, column=0)

        # Third textbox
        self.endDate = Entry(self.master)
        self.endDate["width"] = 30
        self.endDate.focus_set()
        self.endDate.grid(row=3, column=0)

        # Create button to prompt for file location
        self.open_file = Button(
            self.master,
            text="Browse...",
            command=self.browse_file)  # see: def browse_file(self)
        # put it beside the filelocation textbox
        self.open_file.grid(row=1, column=1)

        # Create Start Date Label
        label02 = "Enter Start Date in YYYY-MM-DD format"
        Label(self.master, text=label02).grid(row=2, column=1)

        # Create End Date Label
        label03 = "Enter End Date in YYYY-MM-DD format"
        Label(self.master, text=label03).grid(row=3, column=1)

        # now for a button
        self.submit = Button(
            self.master,
            text="Get Weather!",
            command=self.start_processing,
            fg="red")
        self.submit.grid(row=4, column=0)

    def start_processing(self):
        file = self.filename
        start = self.startDate.get()
        end = self.endDate.get()

        # Perform the getWeather module functions
        fileWithFips = getWeather.addFips(file)
        listOfFips = getWeather.createFipsList(fileWithFips)
        withFips = getWeather.addSummaryData(
            fileWithFips,
            listOfFips,
            start,
            end)
        getWeather.dissolveStats(withFips, file)
        # Kill program when successful
        root.destroy()

    def browse_file(self):
        # put the result in self.filename
        self.filename = tkFileDialog.askopenfilename(title="Open a file...")

        # this will set the text of the self.filelocation
        self.filelocation.insert(0, self.filename)

root = Tk()
app = App(root)
root.mainloop()
