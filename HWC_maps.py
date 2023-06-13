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

from matplotlib import pyplot as pl
import numpy as np
import geopandas as gpd
    
def Mapplot(d,c,map):
    pl.scatter(d['Lon'],d['Lat'],c=c,s=30,alpha=0.3)
    pl.scatter(d['Lon'],d['Lat'],c=c,s=3,alpha=1)
    pl.text(d['Lon'],d['Lat'],'  %s'%d['city'])
    
def PlotMap(CityList,colors='rbgm'):
    worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    fig, ax = pl.subplots(figsize=(12, 6))
    worldmap.plot(color="darkgrey", ax=ax)

    for city,c in zip(CityList,colors):
        Mapplot(city,c,map)

    pl.savefig('Map.png',dpi=300)


