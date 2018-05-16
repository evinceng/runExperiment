# -*- coding: utf-8 -*-
"""
Created on Wed May 16 10:49:25 2018

@author: evin
"""

def traceToFile(traceFileName, string):
    if traceEnabled:
        traceFileName.write("{}".format(string))
    else:
        print "{}".format(string)
        
def traceToFileEOL(traceFileName, string):
    if traceEnabled:
        traceFileName.write("{}".format(string) + "\n")
    else:
        print "{}".format(string) + "\n"

def traceToFileLists(traceFileName, itemList, listName, itemName):
    if itemList:
        traceToFileEOL(traceFileName, listName)
        for item in itemList:
            traceToFileEOL(traceFileName, itemName + str(item))
        traceToFileEOL(traceFileName, "")

def constructProjectionFileds(getID = False):
    fields = { }
    if not getID:
        fields["_id"] = 0
        
    for field in projectionFields:
        fields[field] = 1
        
    return fields

def constructQuery():
    query = { }
    
    if userNames:
        query["userName"] = { "$in": userNames }
        
    if sessions:
        query["sessionID"] = { "$in": sessions }
        
    if relativeTime:
        query["relativeTime"] = { "$gt": relativeTime[0], "$lt": relativeTime[1] }
        
    #print query
    
    return query

def interpolateAndPlot(xIn, yIn, tIn, tMin, tMax, k, Ts, fCode):
#    tIn = timeStamps#np.array(timeStamps)
#    xIn = coordX#np.array(coordX)
#    yIn = coordY#np.array(coordY)
    interpolatedXOnTime = interpolateBS(tIn, xIn, tMin, tMax, k, Ts, fCode)
    interpolatedYOnTime = interpolateBS(tIn, yIn, tMin, tMax, k, Ts, fCode)
    
    sampledTime = np.linspace(tMin, tMax, 1000)
    interpolatedXOnSampledTime = splev(sampledTime, interpolatedXOnTime)
    interpolatedYOnSampledTime = splev(sampledTime, interpolatedYOnTime)
    
    fig = plt.figure()
    ax = fig.gca() 
    ax.scatter(xIn, yIn, c=tIn, cmap=cm.seismic)
    ax.plot(interpolatedXOnSampledTime, interpolatedYOnSampledTime, color="green")
    ax.legend()
    plt.show()     
# ===========================================================================================================        
## 1. Short description -------------------------------------------------------------------------------------
# @brief An analysis to see two circles on a graph via interpolating two users rolling eyes eyeGaze information through time  
# @author EvinA
# @time 2018-05-16


# ===========================================================================================================
## 2. Configuration, libraries -----------------------------------------------------------------------------
# Data
abs_path = "C:\Users\evin\Documents\GitHub\experiment"

# Functions

# Trace files 
rel_path = ""
coreTraceFileName = "_RollingEyes_trace.txt"
traceEnabled = True

# Load libraries -------------------------------------------------------------------------------------------
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import sys
import os
import platform
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from scipy.interpolate import splev
from interpolate_funs import interpolateBS 
from datetime import datetime

# ===========================================================================================================
# 3. Experimental design ---------------------------------------------------------------------------------------

# Database connection Parameters
host = "localhost"
port = 27017

# evina Configuration
userName1 = "evina"
Ts = 0.5 # Sampling frequency
fCode = 1
k = 3 
tMin = 1.6
tMax = 5

# user2 Configuration
userName2 = "user2"
TsUser = 0.5 # Sampling frequency
fCodeUser = 1
kUser = 3 
tMinUser = 3 # 1.49
tMaxUser = 9 # 10.2

# fieldNames variables
xCoordVariable = "leftGaze:x"
yCoordVariable = "leftGaze:y"
timeStampVariable = "relativeTime"
colorUponVariable = "relativeTime"
userNameVariable = "userName"

# query variables
userNames = [ userName1, userName2] # "evina", "user2",
sessions = [ ] #  "evina2018-05-10 14:33:21.185000", "user22018-05-14 12:06:23.842000",
projectionFields = [ "userName", "relativeTime", "leftGaze:x", "leftGaze:y" ]
relativeTime = [ ] # start, end # it will get all times if not provided

# ============================================================================================================
# 4. Load data & trace files ---------------------------------------------------------------------------------
    
# Establish db connection & load data

try:
    client = MongoClient(host=host, port=port)
except ConnectionFailure, e:
    sys.stderr.write("Could not connect to MongoDB: %s" % e)
    sys.exit(1)
        
dbh = client["mediaExposureTry"]
collection = dbh["eyesRolling"]

projection = constructProjectionFileds()
query = constructQuery()
    
resultList = list(collection.find( query, projection))

# construct users empty dict-----------------------------------------------
users = { }
for userName in userNames:
    users[userName] = { }
    for field in projectionFields:
        if field != userNameVariable:
            users[userName][field] = [info[field] for info in resultList if info[userNameVariable] == userName]
#=========================================================================
            
xCoord = users[userName1][xCoordVariable]
yCoord = users[userName1][yCoordVariable]
timeStamps = users[userName1][timeStampVariable]

xCoordUser = users[userName2][xCoordVariable]
yCoordUser = users[userName2][yCoordVariable]
timeStampsUser = users[userName2][timeStampVariable]
    
# Create trace file
currentTime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
#traceFileName = abs_path + rel_path + currentTime + coreTraceFileName
if traceEnabled:
    path = os.path.abspath(os.path.join(abs_path, currentTime + coreTraceFileName))
    traceFileName = open(path, "w")


# =============================================================================================================
# 5. Report ---------------------------------------------------------------------------------------------------
# Basics
traceToFileEOL(traceFileName, "An analysis to see two circles on a graph via interpolating two users eyeGaze information taken from Tobii eyetracker through time, while rolling eyes")
traceToFileEOL(traceFileName, "Time: " + currentTime)
traceToFileEOL(traceFileName, "OS: " + platform.system())
traceToFileEOL(traceFileName, "Python ver: " + platform.python_version())

# Experimental design
traceToFileEOL(traceFileName, "")
traceToFileLists(traceFileName, userNames, "Extracted Users:", "User: ")
traceToFileLists(traceFileName, sessions, "Extracted Sessions:", "Session: ")
traceToFileLists(traceFileName, projectionFields, "Extracted Fileds:", "Field: ")
traceToFileLists(traceFileName, relativeTime, "Extracted Time Period:", "relativeTime: ")


# ============================================================================================================
# 6. Implement Experiment --------------------------------------------------------------------------------------------

interpolatedXOnTime = interpolateBS(timeStamps, xCoord, tMin, tMax, k, Ts, fCode)
interpolatedYOnTime = interpolateBS(timeStamps, yCoord, tMin, tMax, k, Ts, fCode)
    
sampledTime = np.linspace(tMin, tMax, 1000)
interpolatedXOnSampledTime = splev(sampledTime, interpolatedXOnTime)
interpolatedYOnSampledTime = splev(sampledTime, interpolatedYOnTime)
    
interpolatedXOnTimeUser = interpolateBS(timeStampsUser, xCoordUser, tMinUser, tMaxUser, kUser, TsUser, fCodeUser)
interpolatedYOnTimeUser = interpolateBS(timeStampsUser, yCoordUser, tMinUser, tMaxUser, kUser, TsUser, fCodeUser)
    
sampledTimeUser = np.linspace(tMinUser, tMaxUser, 1000)
interpolatedXOnSampledTimeUser = splev(sampledTimeUser, interpolatedXOnTimeUser)
interpolatedYOnSampledTimeUser = splev(sampledTimeUser, interpolatedYOnTimeUser)

# Plot figures
fig = plt.figure()
ax = fig.gca() 
ax.scatter(xCoord, yCoord, c=timeStamps, cmap=cm.seismic)
ax.scatter(xCoordUser, yCoordUser, c=timeStampsUser, cmap=cm.PiYG)
ax.plot(interpolatedXOnSampledTime, interpolatedYOnSampledTime, color="green")
ax.plot(interpolatedXOnSampledTimeUser, interpolatedYOnSampledTimeUser, color="yellow")
ax.legend()
plt.show()
figPath = os.path.abspath(os.path.join(abs_path, currentTime + "_RollingEyes.pdf"))
plt.savefig(figPath)

## Close trace files -------------------------------------------------------------------------------------------------
if traceEnabled:
    traceFileName.close()

