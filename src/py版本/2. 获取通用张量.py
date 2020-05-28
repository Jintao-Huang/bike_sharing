# -----------------------------------------------------------------------
# author: Huang Jintao
# date: 2020-5-10
#
# 该文件功能:
# 1. 获取通用张量start_out, end_in. shape(*区域, 时间)的3dim张量
#   只取北京核心区的经纬度: 因为此区域外的区域单车使用率极低，被忽略计算。(经过缜密计算后选择)
#       纬度范围: [39.66, 40.17]. 精确范围: [39.66133117675781 40.17082214355469]
#       经度范围: [116.06, 116.73]. 精确范围: [116.06025695800781 116.73042297363281]
#       时间范围: 2017-05-10 0:00:00 - 2017-05-17 0:00:00. 半小时切一份.
#           使用floor(例如7:00代表7:00-7:30). 2 * 24 * 7 = 336
#   start_out: shape(371, 488, 336). 某点含义: 当前时间段, 该区域单车使用量(-)
#   end_in: shape(371, 488, 336). 某点含义: 当前时间段, 该区域单车归还量(+)


# -----------------------------------------------------------------------
import pandas as pd
import numpy as np

data = pd.read_pickle("files/节选.pkl")

# 1. 获取通用张量start_out, end_in. shape(371, 488, 336)
latitude_start_arr = data["latitude_start"].to_numpy()
longitude_start_arr = data["longitude_start"].to_numpy()
latitude_end_arr = data["latitude_end"].to_numpy()
longitude_end_arr = data["longitude_end"].to_numpy()
starttime_arr = data["starttime"].to_numpy()
endtime_arr = data["endtime"].to_numpy()

start_out = np.zeros((371, 488, 336), dtype=np.int16)  # (-)
end_in = np.zeros((371, 488, 336), dtype=np.int16)  # (+)
# -------------------- 常数设置:
interval = 0.001373291015625
latitude_0 = 39.66133117675781
longitude_0 = 116.06025695800781
# --------------------
for idx, latitude_start, longitude_start, latitude_end, longitude_end, starttime, endtime in \
        zip(
            range(len(latitude_start_arr)),
            latitude_start_arr, longitude_start_arr, latitude_end_arr, longitude_end_arr, starttime_arr, endtime_arr
        ):
    # ---------------- 计算对应映射的idx: i j k
    i = int((latitude_start - latitude_0) / interval)
    j = int((longitude_start - longitude_0) / interval)
    k = int((starttime - pd.Timestamp(year=2017, month=5, day=10).to_numpy())
            / pd.Timedelta(hours=0.5).to_numpy())
    if 0 <= i < start_out.shape[0] and 0 <= j < start_out.shape[1] and 0 <= k < start_out.shape[2]:
        start_out[i, j, k] -= 1  # 使用. 骑出去

    i = int((latitude_end - latitude_0) / interval)
    j = int((longitude_end - longitude_0) / interval)
    k = int((endtime - pd.Timestamp(year=2017, month=5, day=10).to_numpy())
            / pd.Timedelta(hours=0.5).to_numpy())
    if 0 <= i < end_in.shape[0] and 0 <= j < end_in.shape[1] and 0 <= k < end_in.shape[2]:
        end_in[i, j, k] += 1  # 归还. 骑进来

    if idx % 10000 == 0:
        print("\r>> %d / %d" % (idx + 1, len(latitude_start_arr)), end="")
print("\r>> %d / %d" % (len(latitude_start_arr), len(latitude_start_arr)))

print("start_out: min: %d" % np.min(start_out))  # -54
print("end_in: max: %d" % np.max(end_in))  # 81
pd.to_pickle(start_out, "files/start_out.pkl")
pd.to_pickle(end_in, "files/end_in.pkl")
