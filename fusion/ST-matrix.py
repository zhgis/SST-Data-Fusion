import numpy as np
import cv2
import time
# initial definition
# MERSI 1km
ori = -999
row = 11000
line = 13000
s_lon = 40
e_lon = 170
s_lat = -60
e_lat = 50
dis = 0.01

# AGRI 4km
fy_row = 2750
fy_line = 3250
fy_dis = 0.04

Lon = np.loadtxt('../middle_result/position/Lon.txt')
Lat = np.loadtxt('../middle_result/position/Lat.txt')

start_time = time.time()
# h is the number of fusion days
for h in range(0,15):
    hour_cal = str(h+1).zfill(2)
    # load AGRI data
    FY_SST = np.load('../middle_result/fy4a_reset/fy4a01'+hour_cal+'.npy')
    print(FY_SST.shape)
    SST_data = np.loadtxt('../middle_result/fy3e_resample/pre_pic_'+hour_cal+'.txt')
    SST_data_time = np.loadtxt('../middle_result/fy3e_resample/pre_pic_time_'+hour_cal+'.txt')
    m_sst, n_sst = SST_data.shape

    # Space_weight calculate
    Space_weight = np.zeros((row, line))
    for i in range(m_sst):
        for j in range(n_sst):
            row_n = row - int((Lat[i][j] - s_lat) / dis) - 1
            line_n = int((Lon[i][j] - s_lon) / dis)
            fy_row_n = fy_row - int((Lat[i][j] - s_lat) / fy_dis) - 1
            fy_line_n = int((Lon[i][j] - s_lon) / fy_dis)
            # exclude outliers
            if (SST_data[i][j] != -999 and row_n < row and line_n < line and row_n > 0 and line_n > 0 and fy_row_n < fy_row and fy_line_n < fy_line and fy_row_n > 0 and fy_line_n > 0 and
                    FY_SST[int(SST_data_time[i][j])][fy_row_n][fy_line_n] != -999):
                # if space change was calculated for the first time, assign directly
                if (Space_weight[row_n][line_n] == ori):
                    Space_weight[row_n][line_n] = abs(SST_data[i][j] - FY_SST[int(SST_data_time[i][j])][fy_row_n][fy_line_n])
                # if space change was not calculated for the first time, average with existing values
                else:
                    Space_weight[row_n][line_n] = (abs(SST_data[i][j] - FY_SST[int(SST_data_time[i][j])][fy_row_n][fy_line_n]) + Space_weight[row_n][line_n]) / 2.0

    Space_weight = 1.0 / (Space_weight + 1.0)
    Space_weight[Space_weight == 1] = -999
    print('space weight calculation finished')

    # time wight calculate
    Time_weight = np.zeros((row, line))
    size_large = (line, row)
    FY4A_TIME = np.zeros((fy_row, fy_line)) + ori
    for i in range(fy_row):
        for j in range(fy_line):
            sum = 0
            cha = 0
            n = 0
            ping = 0
            for t in range(24):
                if (FY_SST[t][i][j] != -999):
                    sum += FY_SST[t][i][j]
                    n += 1
            if (n != 0):
                ping = sum / n
                for t in range(24):
                    if (FY_SST[t][i][j] != -999):
                        cha += abs(FY_SST[t][i][j] - ping)
                FY4A_TIME[i][j] = cha / n

    Time_weight = cv2.resize(FY4A_TIME, size_large, interpolation=cv2.INTER_NEAREST)
    Time_weight = 1.0 / (Time_weight + 1.0)
    Time_weight[Time_weight == 1] = -999
    print('time weight calculate finished')
    np.save('../middle_result/weight/Space_weight_' + hour_cal, Space_weight)
    np.save('../middle_result/weight/Time_weight_' + hour_cal, Time_weight)

    ST_weight = np.multiply(Space_weight, Time_weight)
    ST_weight[ST_weight == 998001] = -999
    ST_weight = np.float16(ST_weight)
    np.save('../middle_result/st_weight/ST_weight_'+hour_cal, ST_weight)
    print('space-time matrix calculate finished')

end_time = time.time()
print(end_time - start_time)





