# -----------------------------------------------------------------------
# author: Huang Jintao
# date: 2020-5-10
#
# 该文件功能:
# 1. 文件以starttime升序排序.
# 2. 添加【经纬度】字段: geohash -> 经纬度
#       latitude_start
#       longitude_start
#       latitude_end
#       longitude_end
# 3. 添加endtime: 通过假定10km/s的骑行速度、starttime以及开始点与终止点的位置，计算endtime.
# 4. 将全部的信息保存成pkl文件: "完整.pkl"
#   全部字段:
#       1. orderid
#       2. userid
#       3. bikeid
#       4. biketype
#       5. starttime
#       6. geohashed_start_loc
#       7. geohashed_end_loc
#       8. latitude_start
#       9. longitude_start
#       10. latitude_end
#       11. longitude_end
#       12. endtime
# ----------------------------------
# 5. 选取2017-05-10 ~ 2017-05-16的数据
#   由于2017-05-17 ~ 2017-05-24的数据存在问题，所以会进行去除. 只使用2017-05-10 ~ 2017-05-16的数据
#   例如:
#       1. 2017-05-17 单天数据缺失
#       2. 2017-05-20 18:07:34-23:35:07 数据丢失
#       3. 2017-05-17 ~ 2017-05-24 数据分布紊乱，毫无规律
#       ...
#
# 6. 保存节选数据，保存为: "节选.pkl"
# -----------------------------------------------------------------------

import pandas as pd
import numpy as np
from utils.geohash import decode_exactly

# 1. 文件以starttime升序排序.
data = pd.read_csv("files/mobike_train_data.csv", dtype={
    "orderid": np.int32,
    "userid": np.int32,
    "bikeid": np.int32,
    "biketype": np.int8,
    "starttime": np.object,  # str
    "geohashed_start_loc": np.object,  # str
    "geohashed_end_loc": np.object,  # str
})
data["starttime"] = pd.to_datetime(data["starttime"], format="%Y-%m-%d %H:%M:%S")
data.sort_values("starttime", axis=0, ascending=True, inplace=True)
data.reset_index(drop=True, inplace=True)
# 2. 添加【经纬度】字段: geohash -> 经纬度
# 2.1 获取数据
data['latitude_start'] = pd.Series(dtype=np.float64)
data['longitude_start'] = pd.Series(dtype=np.float64)
data['latitude_end'] = pd.Series(dtype=np.float64)
data['longitude_end'] = pd.Series(dtype=np.float64)
geohashed_start_loc_arr = data['geohashed_start_loc'].to_numpy()
geohashed_end_loc_arr = data['geohashed_end_loc'].to_numpy()
latitude_start_arr = data["latitude_start"].to_numpy()
longitude_start_arr = data["longitude_start"].to_numpy()
latitude_end_arr = data["latitude_end"].to_numpy()
longitude_end_arr = data["longitude_end"].to_numpy()

# 2.2 geohash -> 经纬度
for i in range(data.shape[0]):
    latitude_start, longitude_start, _, _ = decode_exactly(geohashed_start_loc_arr[i])
    latitude_end, longitude_end, _, _ = decode_exactly(geohashed_end_loc_arr[i])
    latitude_start_arr[i] = latitude_start
    longitude_start_arr[i] = longitude_start
    latitude_end_arr[i] = latitude_end
    longitude_end_arr[i] = longitude_end
    if i % 10000 == 0:
        print("\r>> %d / %d" % (i + 1, data.shape[0]), end="")
print("\r>> %d / %d" % (data.shape[0], data.shape[0]))
# 由此可得: error = 0.0006866455078125, 每个单元格间距: 0.001373291015625

# 3. 添加endtime
starttime = data['starttime'].to_numpy()
# 在北京(以下数据为大概数):
#   1经度 = 85.24057242392219km
#   1维度 = 111.11111111111111km
# 公式:
#   地球周长 = 40000km
#   1纬度 = 地球周长 / 360
#   1经度 = cos(当前纬度) * 地球周长 / 360
#   北京纬度 约为39.9度

distance = np.abs(longitude_end_arr - longitude_start_arr) * 85.24057242392219 + \
           np.abs(latitude_end_arr - latitude_start_arr) * 111.11111111111111  # 骑行距离 km
speed = 10  # km/h.  10-12km/h, 计算红绿灯 所以时速设为10km/h
endtime = starttime + distance / speed * pd.Timedelta(hours=1)
data['endtime'] = endtime

# 4. 将全部的信息保存成pkl文件: "完整.pkl"
print(data.dtypes)
print("数据量: %d" % data.shape[0])
pd.to_pickle(data, "files/完整.pkl")
# Out:
# orderid                         int32
# userid                          int32
# bikeid                          int32
# biketype                         int8
# starttime              datetime64[ns]
# geohashed_start_loc            object
# geohashed_end_loc              object
# latitude_start                float64
# longitude_start               float64
# latitude_end                  float64
# longitude_end                 float64
# endtime                datetime64[ns]
# dtype: object
# 数据量: 3214096
# ----------------------------------
# 5. 只使用2017-05-10 ~ 2017-05-16的数据
# data = pd.read_pickle("files/完整.pkl")
starttime = data['starttime'].to_numpy()
idx_max = np.max(np.nonzero(starttime <= pd.Timestamp(year=2017, month=5, day=17).to_numpy())[0])
data = data.iloc[:idx_max + 1, :]  # 由于是升序排序的
# 6. 保存节选数据，保存为: "节选.pkl"
pd.to_pickle(data, "files/节选.pkl")
