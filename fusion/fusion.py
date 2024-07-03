# Fusing data for 24 hours in 15 days
import multiprocessing
import math
import numpy as np
import time
from multiprocessing import Pool, RawArray

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
m_sst = row
n_sst = line
matrix_len = 7
block = 1000

# Number of multi-core blocks
# 11
block_m = m_sst / block
# 13
block_n = n_sst / block
total = block_m * block_n

sst = []

Lon = np.zeros((row,line))
Lat = np.zeros((row,line))
for i in range (row):
    for j in range (line):
        Lon[i][j] = s_lon+j*dis
        Lat[i][j] = e_lat-i*dis

def dis_set(len, dis_a, Dis_weight):
    cen = int(len/2)
    for i in range(len):
        for j in range(len):
            Dis_weight[i][j] = math.sqrt((i-cen)*(i-cen)+(j-cen)*(j-cen))
    Dis_weight = 1.0/(Dis_weight/dis_a + 1)

var_dict = {}

def init_worker(ST_weight, Time_change, X_shape):
    var_dict['ST_weight'] = ST_weight
    var_dict['Time_change'] = Time_change
    var_dict['X_shape'] = X_shape

def worker_func(block_num):
    ST_weight = np.frombuffer(var_dict['ST_weight']).reshape(var_dict['X_shape'])
    Time_change = np.frombuffer(var_dict['Time_change']).reshape(var_dict['X_shape'])
    Dis_weight = np.zeros((matrix_len, matrix_len))
    cen = int(matrix_len / 2)
    dis_set(matrix_len, 1, Dis_weight)
    m_i = int(block_num / block_n)
    n_i = int(block_num % block_m)

    row_list = []
    line_list = []
    pre_sst_list = []

    for i in range(m_i * block, (m_i + 1) * block - matrix_len):
        for j in range(n_i * block, (n_i + 1) * block - matrix_len):
            # multi-core block processing
            ori_matrix = ST_weight[i:i + matrix_len, j:j + matrix_len]
            diff = Time_change[i:i + matrix_len, j:j + matrix_len]
            # set null(999) to 0 ，998001 = 999*999
            ori_matrix[ori_matrix == 998001] = 0
            ori_matrix[diff == -999] = 0
            multi_matrix = np.multiply(ori_matrix, Dis_weight)
            sum_matrix = np.sum(multi_matrix)
            # set outliers to 0, not included in the fusion calculation
            if (sum_matrix == 0):
                row_list.append(i + cen)
                line_list.append(j + cen)
                pre_sst_list.append(-999)
                # if sum number is 0 , fusion result is -999
            # else set the fusion result to np.multiply(multi_matrix, diff))
            else:
                row_list.append(i + cen)
                line_list.append(j + cen)
                multi_matrix = multi_matrix / sum_matrix
                pre_sst_list.append(np.sum(np.multiply(multi_matrix, diff)))
    return row_list, line_list, pre_sst_list

if __name__ == '__main__':
    print('fusion project start')
    start_time = time.time()
    # h is the number of fusion days
    for h in range (9,10):
        day_cal = str(h + 1).zfill(2)
        X_shape = (row, line)
        ST_weight_load = np.load('../middle_result/st_weight/ST_weight_' + day_cal+'.npy')
        m_sst = row
        n_sst = line
        # load FY-4A AGRI data
        FY_SST = np.load('../middle_result/fy4a_reset/fy4a01' + day_cal+'.npy')
        # create a shred matrix and assign values
        ST_weight_X = RawArray('d', X_shape[0] * X_shape[1])
        # Wrap X as an numpy array so we can easily manipulates its data.
        ST_weight_X_np = np.frombuffer(ST_weight_X).reshape(X_shape)
        # Copy data to our shared array.
        np.copyto(ST_weight_X_np, ST_weight_load)

        Time_change_X = RawArray('d', X_shape[0] * X_shape[1])
        Time_change_X_np = np.frombuffer(Time_change_X).reshape(X_shape)
        Time_change = np.zeros((row, line)) + ori

        # load FY-3E MERSI data
        SST_data = np.loadtxt('../middle_result/fy3e_resample/pre_pic_' + day_cal + '.txt')
        SST_data_time = np.loadtxt('../middle_result/fy3e_resample/pre_pic_time_' + day_cal + '.txt')

        print('DATA load finished ,  multi-core data distribution and fusion start')
        for h_time in range(0,24):
            pre_hour = str(h_time).zfill(2)
            for i in range(m_sst):
                for j in range(n_sst):
                    fy_row_n = (fy_row - int((Lat[i][j] - s_lat) / fy_dis) - 1)-1
                    fy_line_n = (int((Lon[i][j] - s_lon) / fy_dis))-1
                    # 超出范围的数据进行排除，注意yh和fy的异常值
                    if (SST_data[i][j] != -999 and fy_row_n < fy_row and fy_line_n < fy_line and fy_row_n > 0 and fy_line_n > 0 and
                            FY_SST[int(SST_data_time[i][j])][fy_row_n][fy_line_n] != -999 and
                            FY_SST[int(pre_hour)][fy_row_n][fy_line_n] != -999):
                        Time_change[i][j] = SST_data[i][j] + FY_SST[int(pre_hour)][fy_row_n][fy_line_n] - FY_SST[int(SST_data_time[i][j])][fy_row_n][fy_line_n]

            np.copyto(Time_change_X_np, Time_change)
            cpu_num = multiprocessing.cpu_count()
            # fusion
            with Pool(processes=cpu_num, initializer=init_worker,
                      initargs=(ST_weight_X, Time_change_X, X_shape)) as pool:
                sst_sum = pool.map(worker_func, range(int(total)))
            Pre_pic = np.zeros((row, line)) + ori
            # merge multi-core blocks
            for n in range(len(sst_sum)):
                for i in range(len(sst_sum[n][0])):
                    Pre_pic[sst_sum[n][0][i]][sst_sum[n][1][i]] = sst_sum[n][2][i]
            Pre_result = np.float16(Pre_pic)
            np.save('../pre_result_time/pre_pic_multi_'+day_cal+'_' + pre_hour + '.txt', Pre_result)

    end_time = time.time()
    print('fusion ended')
    print(end_time - start_time)
