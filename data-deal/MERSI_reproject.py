
import multiprocessing
import numpy as np
import time
import h5py
import os
from multiprocessing import Pool

# MERSI 1KM
row = 11000
line = 13000
ori = -999
dis = 0.01

# AGRI 4KM
fy_row = 2750
fy_line = 3250
s_lon = 40
e_lon = 170
s_lat = -60
e_lat = 50
fy_dis = 0.04

def cal(file):
    # get time from file name
    file_name = file.split('_')
    time = file_name[8]
    hour = time[0:2]

    row_list = []
    line_list = []
    time_list = []
    sst_list = []
    try:
        f = h5py.File(file, 'r')
        Lon = f['Longitude'][:]
        Lat = f['Latitude'][:]
        SST_data = f['sea_surface_temperature'][:]
        SST_data = SST_data / 100.0
    except Exception as e:
        print(e)
    else:
        yh_Lon_max = np.max(Lon)
        yh_Lon_min = np.min(Lon)
        yh_Lat_max = np.max(Lat)
        yh_Lat_min = np.min(Lat)
        m, n = SST_data.shape

        # exclude data out of range
        if (yh_Lon_max < e_lon and yh_Lon_min > s_lon and yh_Lat_max < e_lat and yh_Lat_min > s_lat):
            print('start re-project')
            for i in range(m):
                for j in range(n):
                    row_n = int((Lat[i][j] - s_lat) / dis)
                    line_n = int((Lon[i][j] - s_lon) / dis)
                    if (SST_data[i][j] != -9.99 and SST_data[i][
                        j] != -8.88 and row - row_n - 1 < row and line_n < line and row_n > 0 and line_n > 0):
                        row_list.append(row - row_n - 1)
                        line_list.append(line_n)
                        sst_list.append(SST_data[i][j])
                        time_list.append(hour)

        else:
            print('not in range')

    return row_list, line_list, sst_list, time_list

if __name__=='__main__':
    fy3e_dir = 'E:/FY3E/'
    cpu_num = multiprocessing.cpu_count()
    print(cpu_num)
    start_time = time.time()
    for h in range(9,10):
        print(h+1)
        day = str(h + 1).zfill(2)

        fy_files = os.listdir(fy3e_dir)
        file_lists = []
        for file in fy_files:
            if (file[37:39]==day):
                ori_file = fy3e_dir + '/' + file
                file_lists.append(ori_file)

            ori_file = fy3e_dir + '/' + file

            file_lists.append(ori_file)

        pool = Pool(processes=1)
        sst_sum = pool.map(cal, file_lists)

        n_len = len(sst_sum)
        Pre_pic = np.zeros((row, line)) + ori
        Pre_pic_time = np.zeros((row, line)) + ori
        # 文件数n
        for n in range(n_len):
            for i in range(len(sst_sum[n][0])):
                Pre_pic[sst_sum[n][0][i]][sst_sum[n][1][i]] = sst_sum[n][2][i]
                Pre_pic_time[sst_sum[n][0][i]][sst_sum[n][1][i]] = sst_sum[n][3][i]
        Pre_pic = np.float16(Pre_pic)
        Pre_pic_time = np.float16(Pre_pic_time)
        np.save('E:/result1/pre_pic_'+day, Pre_pic)
        np.save('E:/result1/pre_pic_time_'+day, Pre_pic_time)


    end_time = time.time()
    print('time：')
    print(end_time - start_time)




