from math import log10

__all__ = ["decode_exactly", "decode", "encode"]

__base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
__decodemap = {}  # dict(str: int)
for i in range(len(__base32)):
    __decodemap[__base32[i]] = i
del i


def decode_exactly(geohash):
    """将geohash解码为它的确切值，包括error误差

    :param geohash: str
    :return: latitude_center: float, longitude_center: float,
            latitude error(+-): float_+, longitude_error(+-): float_+
    """
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)  # 纬度、经度范围
    lat_err, lon_err = 90.0, 180.0  # 17, 18
    is_even = True  # 偶数经度
    # 遍历每一个字符
    for c in geohash:
        # 1. 解码成十进制
        cd = __decodemap[c]  # cd: int [0, 32)
        for mask in [16, 8, 4, 2, 1]:  # 10000, 01000, 00100, 00010, 00001
            if is_even:  # adds longitude info
                lon_err /= 2
                if cd & mask:
                    lon_interval = ((lon_interval[0] + lon_interval[1]) / 2, lon_interval[1])
                else:
                    lon_interval = (lon_interval[0], (lon_interval[0] + lon_interval[1]) / 2)
            else:  # adds latitude info
                lat_err /= 2
                if cd & mask:
                    lat_interval = ((lat_interval[0] + lat_interval[1]) / 2, lat_interval[1])
                else:
                    lat_interval = (lat_interval[0], (lat_interval[0] + lat_interval[1]) / 2)
            is_even = not is_even
    lat = (lat_interval[0] + lat_interval[1]) / 2  # center
    lon = (lon_interval[0] + lon_interval[1]) / 2  # center
    return lat, lon, lat_err, lon_err


def decode(geohash):
    """
    Decode geohash, returning two strings with latitude and longitude
    containing only relevant digits and with trailing zeroes removed.
    """
    lat, lon, lat_err, lon_err = decode_exactly(geohash)
    # Format to the number of decimals that are known
    lats = "%.*f" % (max(1, int(round(-log10(lat_err)))) - 1, lat)
    lons = "%.*f" % (max(1, int(round(-log10(lon_err)))) - 1, lon)
    if '.' in lats:
        lats = lats.rstrip('0')
    if '.' in lons:
        lons = lons.rstrip('0')
    return lats, lons


def encode(latitude, longitude, precision=12):
    """
    Encode a position given in float arguments latitude, longitude to
    a geohash which will have the character count precision.
    """
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0  # 2进制的idx
    ch = 0  # 10进制
    even = True  # 偶数
    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= bits[bit]
                lon_interval = (mid, lon_interval[1])
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= bits[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash += __base32[ch]
            bit = 0
            ch = 0
    return ''.join(geohash)

