#!/usr/bin/env python
# coding: utf-8

# # Hydrology of World Cities
# 
# By Andrew Ireson(1) and Simon Mathias(2)
# 
# 1. Global Institute for Water Security, University of Saskatchewan, Canada
# 2. University of Durham, UK
# 
# ## Usage
# 
# Run every block of code to import libraries and load functions. To modify cities, edit the block of code below the title "Run the Script:". 
# 
# 
# ## To do:
# 
# * Refactor the code so that the user input is more intuitive and the plot functions do not need to be modified if the number of cities is modified.

from matplotlib import pyplot as pl
import numpy as np
from mpl_toolkits.basemap import Basemap
import json
import urllib
import sys
import matplotlib as mpl
mpl.style.use('ggplot')
mpl.style.use('seaborn-notebook')

# Function to get city altitudes
from geopy.geocoders import Nominatim
geocode=Nominatim().geocode

    
def Mapplot(d,c,map):
    map.plot(d['Lon'],d['Lat'],'o'+c,alpha=0.3,markersize=8,latlon=True)
    map.plot(d['Lon'],d['Lat'],'.'+c,markersize=5,latlon=True)
    
def PlotMap(CityList,colors='rbgm'):
    pl.figure(figsize=(6,6))
    map = Basemap(projection='merc',llcrnrlon=-185.,urcrnrlon=185.,llcrnrlat=-60,urcrnrlat=80.,rsphere=(6378137.00,6356752.3142))
    # map.drawrivers(linewidth=0.25,color='blue')
    map.drawcoastlines(linewidth=0.5)
    # map.drawcountries(linewidth=0.5)
    # map.drawstates()
    for city,c in zip(CityList,colors):
        Mapplot(city,c,map)

    pl.savefig('Map.png',dpi=300)




