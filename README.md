# Spatiotemporal Sea Surface Temperature Data Fusion Model for MERSI and AGRI Sensors

# Dir list

--data (Store files including MERSI and AGRI SST product data on Jan 10, 2023, AGRI latitude and longitude lookup table data, and buoy argo data from January 2023)

--data-deal (1.AGRI_reset.py Reconstruct original AGRI SST data ; 2. MERSI_reset.py reproject MERSI data to 0.01°x0.01°grid)

--fusion (1.ST-matrix.py calculate spectral weight and time weight factor and calculate the matrix obtained by multiplying them ; 2.fusion.py do the multi-core fusion  )

--fusion_result (Store fusion result on Jan 10, 2023)

--middle_result (Store middle result calculated by data-deal procedure)

--valid (1.15days_validation.py valid 15 days result with argo buoy data ; 2.draw_valid.py  draw valid_reslut ; 3.valid_fy3e_fusion_415.txt give a result of January 2023, run the draw_valid.py to see the valid PNG)

# Process

for data fusion of Jan 10 , 2023 for 24 hours

1. run data-deal/AGRI_reset.py get midddle_result/fy4a_reset/fy4a0110.npy
   
2. run data-deal/MERSI_reproject.py get midddle_result/fy3e_resample/pre_pic_10.npy and pre_pic_time_10.npy
   
3. run fusion/ST_matrix.py get midddle_result/st_weight/ST_weight_10.npy
   
4. run fusion/fusion.py get fusion_result/pre_pic_multi_10_00.npy pre_pic_multi_10_01.npy pre_pic_multi_10_02.npy....pre_pic_multi_10_23.npy

5. run valid/ 15days_valid.py get valid.txt , run draw_valid get valid.png

# Attention
Because of the large amount of raw data, we have provided 1 day of original data （Jan 10, 2023）and fusion process data and result data, and also the validation program. 
We have uploaded the validation result of 15 days fusion results, you can run the program draw_valid.py in the valid folder to check the validation results.
When running the fusion program, please note that it corresponds to the location of our folder, using relative file addresses, and note that the number of days to be fused in the fusion.py file should be changed h parameter to match the corresponding data.

# Files are compressed due to storage space limitations, please unzip all rar files before use.

We give sample data, full data can be downloaded from the website http://satellite.nsmc.org.cn.
