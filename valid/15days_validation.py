import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cfeat
import cartopy.io.shapereader as shapereader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from netCDF4 import Dataset
import os
lon_path = '../middle_result/position/Lon.txt'
lat_path = '../middle_result/position/Lat.txt'
SST_Lon = np.loadtxt(lon_path)
SST_Lat = np.loadtxt(lat_path)
min_lon = np.min(SST_Lon)
max_lon = np.max(SST_Lon)
min_lat = np.min(SST_Lat)
max_lat = np.max(SST_Lat)

for h in range (15):
    pre_c = []
    argo_c = []
    lon_c = []
    lat_c = []
    Q_c = []
    fy3e_hour = []
    argo_hour = []
    print(h)
    site = str(h+1).zfill(2)
    # 定义1km分辨率空间跨度
    dis = 0.01
    # argo浮标数据处理
    path = '../data/argo/202301' + site + '_prof.nc'
    dst = Dataset(path, mode='r', format="netCDF4")
    all_vars = dst.variables.keys()
    # print(all_vars)
    # 取采样时间，例如有73个采样点，得到每个的采样时间
    Time = dst.variables['JULD'][:]
    Time_location = dst.variables['JULD_LOCATION'][:]
    # 获取经纬度
    Lon = dst.variables['LONGITUDE'][:]
    Lat = dst.variables['LATITUDE'][:]
    Temp_QC = dst.variables['PROFILE_TEMP_QC'][:]
    Type = dst.variables['PLATFORM_TYPE'][:]
    # 获取温度值，温度值分为1010垂直层，取第一层
    temp = dst.variables['TEMP'][:]
    print(temp.shape)
    temp1 = temp[:, 0]
    print(temp1.shape)
    valid_len = 3
    # # 对每个采样点进行处理
    for i in range(0, Time_location.shape[0]):
        # 获取该点的经纬度和采样时间
        lon = Lon[i]
        lat = Lat[i]
        time = Time_location[i]
        # 时间转化为UTC时间，获取小时和分钟
        hour = int(((time - int(time)) * 24 + 8) % 24)
        min = int(((time - int(time)) * 1440) % 60)
        hour = str(hour)
        hour = hour.zfill(2)
        sst_path = '../fusion_result/pre_pic_multi_' + site + '_' + hour + '.npy'
        SST = np.load(sst_path)
        m,n = SST.shape

        # 以栅格形式验证
        # 读取txt数据
        # 确定小时，添加到一起，如果argo数据采样点位置在影像范围内，则计算
        if (lon > min_lon and lon < max_lon and lat > min_lat and lat < max_lat):

            # 匹配到对应的栅格
            line_index = int((lon - min_lon) / dis)
            row_index = m - int((lat - min_lat) / dis) - 1
            sum = 0.0
            num = 0.0
            pre = -999.0
            value_dis=999
            # 取5*5栅格内平均值
            for ni in range(-valid_len, valid_len):
                for nj in range(-valid_len, valid_len):
                    if (row_index + ni>=0 and row_index + ni<m and line_index + nj>=0 and line_index + nj<n and abs(SST[row_index + ni][line_index + nj]-temp1[i])<3):
                        if (SST[row_index + ni][line_index + nj] != -999 ):

                            sum += SST[row_index + ni][line_index + nj]
                            num += 1.0

            if (num != 0):
                pre = sum/num
            print('hour: ', hour)
            print('pre: ', pre)
            print('argo: ', temp1[i])
            print('argo_site: ', lon, lat)
            print('pre_site: ', SST_Lon[row_index][line_index], SST_Lat[row_index][line_index])
            print('argo_SST: ', temp1[i])
            print('platform type: ', Type[i])
            print('temp_QC: ', Temp_QC[i])


            pre_c.append(pre)
            argo_c.append(temp1[i])
            lon_c.append(lon)
            lat_c.append(lat)
            Q_c.append(Temp_QC[i])
            # 保存结果
            print('next')

    Note = open('valid_fy3e_fusion_today.txt', mode='a')
    for i in range(0, len(pre_c)):
        Note.writelines(
            [str(pre_c[i]) + ' ', str(argo_c[i]) + ' ',   str(lon_c[i]) + ' ', str(lat_c[i]) + ' ', '\n'])  # \n 换行符\
    Note.close()

