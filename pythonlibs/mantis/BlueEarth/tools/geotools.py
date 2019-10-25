#coding:utf-8

"""
geotools.py
坐标转换
逆地址转换
基站lbs坐标转换
"""
import traceback
import requests

def geocoding_address( lon, lat):
    """
    逆地理编码服务
    refer:
    http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding

    http://api.map.baidu.com/geocoder/v2/?location=39.983424,116.322987&output=json&pois=1&ak=XDFk8RGryIrg3Hd7cr2101Yx
    http://api.map.baidu.com/geocoder/v2/?location=39.983424,116.322987&output=json&pois=0&ak=XDFk8RGryIrg3Hd7cr2101Yx

    :param lon:
    :param lat:
    :return:

    ak ='2lGY892LYZokThGF0Ie1FoXjIxaBFNi4'
    """
    ak ='XDFk8RGryIrg3Hd7cr2101Yx'
    # ak = self.cfgs.get('ak')
    url = "http://api.map.baidu.com/geocoder/v2/"
    params = {
        'location': "%s,%s" % (lat, lon),
        'output': 'json',
        'pois': 0,
        'ak': ak
    }
    address = ''
    try:
        resp = requests.get(url, params)
        data = resp.json().get('result', {})
        address = data.get('formatted_address', '')
    except:
        traceback.print_exc()
        # instance.getLogger().error("<%s> geocoding failed!" % (self.name,))
    return address


def wgs84_to_gcj02(x, y):
    import coord_transform
    return coord_transform.wgs84_to_gcj02(x,y)
    # convert gps coordinates to map coordinates
    # returns: None if invalid convertion, else (mapx,mapy) be back
    from math import sin, cos, sqrt
    if x * y == 0:
        return 0, 0

    a1 = x
    a2 = y

    # long double v4; // st3@1
    # double v5; // st4@1
    # long double v6; // st5@1
    # double v7; // st6@1
    # double v8; // st7@1
    # long double v9; // st5@1
    # long double v10; // st4@1
    # long double v11; // st3@1
    # long double v12; // st4@1
    # long double v13; // st5@1
    # long double v14; // st4@1
    # __int16 v15; // fps@1
    # char v16; // c0@1
    # int result; // eax@3
    # long double v18; // st3@3
    # double v19; // ST00_8@3
    # long double v20; // st7@3
    # long double v21; // st5@3
    # double v22; // ST10_8@3
    # double v23; // ST08_8@3
    # double v24; // [sp+0h] [bp-18h]@1

    v8 = a1 - 105.0
    v7 = a2 - 35.0
    v9 = (sin((a1 - 105.0) * 18.84955592153874) + sin((a1 - 105.0) * 6.28318530717958)) * 13.33333333333333
    v10 = sin((a1 - 105.0) * 1.047197551196597)
    v11 = sin((a1 - 105.0) * 0.1047197551196597)
    v24 = (v10 + v10 + sin((a1 - 105.0) * 3.14159265358979)) * 13.33333333333333 + v9 + (
                v11 + v11 + sin((a1 - 105.0) * 0.2617993877991492)) * 100.0
    v12 = sin((a2 - 35.0) * 1.047197551196597)
    v13 = (v12 + v12 + sin((a2 - 35.0) * 3.14159265358979)) * 13.33333333333333 + v9
    v14 = sin((a2 - 35.0) * 0.1047197551196597)
    v6 = v13 + (v14 + v14 + sin((a2 - 35.0) * 0.2617993877991492)) * 106.6666666666667
    v5 = (a2 - 35.0) * (a1 - 105.0) * 0.1
    v4 = a1 - 105.0
    # UNDEF(v15);
    v16 = 0
    if v16:
        v4 = -v4
    v18 = sqrt(v4)
    # result = a3
    v19 = (v8 * 0.1 + 1.0) * v8 + v18 * 0.1 + v7 + v7 + v24 + v5 + 300.0
    v20 = (v7 * 0.2 + 3.0) * v7 + v18 * 0.2 + v8 + v8 + v5 - 100.0 + v6
    v21 = sin(a2 * 0.01745329251994328)
    v22 = 1.0 - v21 * v21 * 0.00669342
    v23 = sqrt(v22)
    a3 = v19 / (cos(a2 * 0.01745329251994328) * 111321.3757488656) * v23 + a1
    a4 = v23 * v20 * v22 * 0.000009043532897409686 + a2
    return (a3, a4)


def gcj02_to_wgs84(x, y):
    a1 = x
    a2 = y
    v5, v6 = wgs84_to_gcj02(a1, a2)
    v5 = a1 + a1 - v5
    v6 = a2 + a2 - v6
    v7, v8 = wgs84_to_gcj02(v5, v6)
    # result = a3;
    a3 = v5 + a1 - v7
    a4 = v6 + a2 - v8
    return (a3, a4)


def test_convert():
    x,y = 121.46916333333333, 31.103391666666667

    print x, y
    x, y = wgs84_to_gcj02(x,y)
    # x, y = point_g2m(121, 0)
    print x, y
    x,y = gcj02_to_wgs84(x,y)
    print x,y
# x,y = point_m2g(x,y)
# print x,y


if __name__ == '__main__':
    # print geocoding_address(121,31.1)
    test_convert()