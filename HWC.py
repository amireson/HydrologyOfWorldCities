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
#from mpl_toolkits.basemap import Basemap
import json
import urllib
import sys
import matplotlib as mpl
mpl.style.use('ggplot')
mpl.style.use('seaborn-notebook')

# # Function to get city altitudes
# from geopy.geocoders import Nominatim
# geocode=Nominatim().geocode


# ## Function: FindCity
# 
# This function searches for a city based on a city name and/or a country name.

# In[ ]:


def FindCity(cityname,country=''):
    # Find city ID from WMO datafile:
    cities=urllib.request.urlopen('https://worldweather.wmo.int/en/json/full_city_list.txt')
    cities.__iter__()
    
    cname=[]
    ccountry=[]
    cid=[]
    for city in cities:
        citystr=str(city)[1:].replace('"','').replace("'","").replace('\\n','')
        if cityname.lower() in citystr.lower():
            citystr=citystr.split(';')
            cid.append(citystr[2])
            cname.append(citystr[1])
            ccountry.append(citystr[0])
    
    if len(ccountry)>1 and country!='':
        for i,c in enumerate(ccountry):
            if country.lower() in c.lower():
                print(cname[i],'-',ccountry[i])
                return cid[i], cname[i], ccountry[i]
    elif len(ccountry)==1:
        cname=cname[0]
        ccountry=ccountry[0]
        cid=cid[0]
        print(cname,'-',ccountry)
    else:    
        [print(i,'-',j) for i,j in zip(cname,ccountry)]
    return cid, cname, ccountry


# ## Function: Get station data
# 
# This function obtains average monthly climate data for a particular city, identified by the WMO city ID, which is returned by FindCity

# In[ ]:


def GetStationData(cid):
    url = "https://worldweather.wmo.int/en/json/%s_en.xml" % cid
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    R=[float(data['city']['climate']['climateMonth'][i]['rainfall']) for i in range(12)]
    Rd=[float(data['city']['climate']['climateMonth'][i]['raindays']) for i in range(12)]
    Tmax=[float(data['city']['climate']['climateMonth'][i]['maxTemp']) for i in range(12)]
    Tmin=[float(data['city']['climate']['climateMonth'][i]['minTemp']) for i in range(12)]
    Lat=float(data['city']['cityLatitude'])
    Lon=float(data['city']['cityLongitude'])
    return R,Rd,Tmax,Tmin,Lat,Lon


# ## Function: Get city altitude
# 
# Using the geopy library

# In[ ]:


def GetCityAltitude(d):
    url = "https://maps.googleapis.com/maps/api/elevation/json?locations=%f,%f&key=%s"
    my_api_key="AIzaSyB9fPCWj2bXeJZ6u0IwYYxKysKXaIXOBe4"
    response = urllib.request.urlopen(url%(d['Lat'],d['Lon'],my_api_key))
    data = json.loads(response.read())
    return data['results'][0]['elevation']


# ## Function: Calculate Potential Evaporation
# 
# Using the FAO56 monthly estimation method, which calculates reference potential evapotranspiration as a function of lattitude, altitude, and monthly minimum and maximum temperature 

# In[ ]:


def PotentialEvaporation(d):
    Elevation=d['Alt']
    Lat=d['Lat']

    dM=np.array([31,28,31,30,31,30,31,31,30,31,30,31])
    doy=np.cumsum(dM)-np.round(dM/2);
    
    PE=np.zeros(12)
    for i in range(12):
        Tmin=d['Tmin'][i]
        Tmax=d['Tmax'][i]
        
        j=Lat*np.pi/180
        kRs=0.16
        Tmean=(Tmax+Tmin)/2.
        Delta=4098*0.6108*np.exp(17.27*Tmean/(Tmean+237.3))/(Tmean+237.3)**2
        P=101.3*((293-0.0065*Elevation)/293.)**5.26
        gamma=0.665e-3*P
        u2=2.
        ea=0.6108*np.exp(17.27*Tmin/(Tmin+237.3))
        eo=0.6108*np.exp(17.27*Tmax/(Tmax+237.3))
        es=(ea+eo)/2.
        Gsc=0.0820
        dr=1+0.033*np.cos(2*np.pi/365*doy[i])
        dell=0.409*np.sin(2*np.pi/365*doy[i]-1.39)
        ws=np.arccos(-np.tan(j)*np.tan(dell))
        sigma=4.903e-9
        A=ws*np.sin(j)*np.sin(dell)+np.cos(j)*np.cos(dell)*np.sin(ws)
        Ra=24*60/np.pi*Gsc*dr*A
        RSO=(0.75+2e-5*Elevation)*Ra
        RS=kRs*np.sqrt(Tmax-Tmin)*Ra
        alpha=0.23
        Rns=(1-alpha)*RS
        Rnl=sigma*((Tmax+273)**4+(Tmin+273)**4)/2*(0.34-0.14*np.sqrt(ea))*(1.35*RS/RSO-0.35)
        Rn=Rns-Rnl
        G=0
        T=Tmean

        PE[i]=(0.408*Delta*(Rn-G)+gamma*900/(T+273)*u2*(es-ea))/(Delta+gamma*(1+0.34*u2))*dM[i]
    
    return list(PE)


# ## Get everything

# In[ ]:


def GetCityData(city,country):
    d={}
    d['cid'],d['city'],d['country']=FindCity(city,country)
    d['R'],d['Rd'],d['Tmax'],d['Tmin'],d['Lat'],d['Lon']=GetStationData(d['cid'])
    d['Alt']=GetCityAltitude(d)
    d['PE']=PotentialEvaporation(d)
    print('Lat: %f, Lon: %f, Alt: %f'%(d['Lat'],d['Lon'],d['Alt']))
    return d


# ## Plotting functions

# In[ ]:


def Rainplot(d,c):
    t=list(range(1,13))
    pl.step([0]+t,[d['R'][0]]+d['R'],color=c,linewidth=1.5,label='%s, Ann. Prec = %.0f mm'%(d['city'][0:16],sum(d['R']))) 

def PEplot(d,c):
    t=list(range(1,13))
    pl.plot([0]+t,[d['PE'][0]]+d['PE'],color=c,linestyle='--',linewidth=1.5,label='%s, Ann. Pot. Evap. = %.0f mm'%(d['city'][0:16],sum(d['PE']))) 

def PlotP_PE(CityList,colors='rbgm'):
    mm='JFMAMJJASOND'
    

    mm=[mon for mon in mm]
    t=list(range(1,13))
    fs=14
    pl.figure(figsize=(12,7))
    pl.axes([0.1, 0.3, 0.8, 0.6])
    for city,c in zip(CityList,colors):
        Rainplot(city,c)
        PEplot(city,c)


    pl.ylabel('Precip (mm/month)',fontsize=fs)
    pl.xlabel('Month',fontsize=fs)
    pl.xticks(np.arange(0.5,12),mm,)
    pl.xlim(0,12)
    pl.legend(fontsize=fs,loc=(0.5,-0.45))
    pl.show()
    #pl.savefig('Precip.png',dpi=300)

def Tempplot(d,c):
    t=list(range(1,13))
    pl.fill_between([0]+t,[d['Tmin'][0]]+d['Tmin'],[d['Tmax'][0]]+d['Tmax'],color=c,alpha=0.5,label=d['city'][0:16]) 
    pl.plot([0]+t,[d['Tmin'][0]]+d['Tmin'],'-'+c,linewidth=2)
    pl.plot([0]+t,[d['Tmax'][0]]+d['Tmax'],'-'+c,linewidth=2)
   
def PlotT(CityList,colors='rbgm'):
    mm='JFMAMJJASOND'
    mm=[mon for mon in mm]
    t=list(range(1,13))
    fs=14
    pl.figure(figsize=(12,7))
    pl.axes([0.1, 0.3, 0.8, 0.6])
    
    for city,c in zip(CityList,colors):
        Tempplot(city,c)

    pl.ylabel('Average temperature range ($^\circ$C)',fontsize=fs)
    pl.xlabel('Month',fontsize=fs)
    pl.xticks(np.arange(0.5,12),mm,)
    pl.xlim(0,12)
    pl.legend(fontsize=fs,loc=(0.5,-0.35))
    pl.show()
    #pl.savefig('Temp.png',dpi=300)

def PrintCityData(city):
    print('   R (mm), PE (mm)')
    mm='JFMAMJJASOND'
    for m,R,PE in zip(mm,city['R'],city['PE']): print('%s, %.1f,   %.1f'%(m,R,PE))
