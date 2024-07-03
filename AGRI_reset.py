import math
import numpy as np
from matplotlib.ticker import MultipleLocator
from netCDF4 import Dataset
import os
import cv2
import h5py
import time
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cfeat
import cartopy.io.shapereader as shapereader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from netCDF4 import Dataset
import pandas as pd
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.stats import linregress
from sklearn.metrics import mean_squared_error, r2_score

# load FY-4A latitude and longitude lookup table
GEO_lon = np.loadtxt("../data/geo/lon.txt")
GEO_lat = np.loadtxt("../data/geo/lat.txt")

# MERSI 1KM
ori = -999
row = 11000
line = 13000
s_lon = 40
e_lon = 170
s_lat = -60
e_lat = 50
dis = 0.01

# AGRI 4KM
fy_row = 2750
fy_line = 3250
fy_dis = 0.04

def f_1(x, A, B):
    return A * x + B

FY_SST = np.zeros((fy_row, fy_line)) + ori
GEO_lon = np.transpose(GEO_lon).reshape(2748, 2748)
GEO_lat = np.transpose(GEO_lat).reshape(2748, 2748)
SST_Lon = np.zeros((fy_row, fy_line))+ori
SST_Lat = np.zeros((fy_row, fy_line))+ori

for i in range(fy_row):
    for j in range(fy_line):
        SST_Lon[i][j] = s_lon + j * fy_dis
        SST_Lat[i][j] = e_lat - i * fy_dis

def resample(SST, FY_SST):
    m, n = GEO_lon.shape
    for i in range(m):
        for j in range(n):
            row = fy_row - int((GEO_lat[i][j] - s_lat) / fy_dis)-1
            line = int((GEO_lon[i][j] - s_lon) / fy_dis)
            if (row < fy_row and row>=0 and line>=0 and line<fy_line):
                FY_SST[row][line] = SST[i][j]
# reproject
for day_index in range(9,10):
    print(day_index)
    print('AGRI data load')
    site = str(day_index + 1).zfill(2)
    sst = []
    for i in range(0, 24):
        day = str(i).zfill(2)
        dir = 'E:/FY/fy4A_data/01' + site
        fy_files = os.listdir(dir)
        for file in fy_files:
            file_name = file.split('_')
            hour_time = file_name[9]
            hour = hour_time[8:10]
            if (hour == str(i).zfill(2)):
                file = dir + '/' + file
                dst = Dataset(file, mode='r', format="netCDF4")
                SST = dst.variables['SST'][:]
                SST = np.array(SST)
                # set outliers to -999
                filter_bad_data = (SST > 65500) | (SST == -888)
                SST[filter_bad_data] = -999
                sst.append(SST)
    SST = np.array(sst)
    # data reset
    for m in range(2748):
        for n in range(2748):
            x = []
            y = []
            point_num = 0
            for h in range(24):
                 if (SST[h][m][n] != -999):
                     x.append(h)
                     point_num += 1
                     y.append(SST[h][m][n])
            x = np.array(x)
            y = np.array(y)
            y3 = x
            if (point_num >= 3):
                A1, B1 = optimize.curve_fit(f_1, x, y)[0]
                y3 = A1 * x + B1
                for h1 in range(24):
                    if (SST[h1][m][n] == -999):
                        SST[h1][m][n] = A1 * h1 + B1
    sst_reset = []
    for j in range(0, 24):
        resample(SST[j][:][:], FY_SST)
        size = (fy_line, fy_row)
        RESIZE_SST = cv2.resize(FY_SST, size, interpolation=cv2.INTER_NEAREST)
        sst_reset.append(RESIZE_SST)


    SST = np.array(sst_reset)
    print(SST.shape)
    SST = np.float16(SST)
    np.save('fy4a01'+site, SST)

