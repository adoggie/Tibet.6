#coding:utf-8

import traceback
import requests
# http://apilocate.amap.com/position?accesstype=0&imei=868120201788186&cdma=0&bts=460,01,9649,28657,35&output=json&key=0b7d114fdc4eb50079408292b7249015
# from coord_transform import gcj02_to_wgs84
from geotools import gcj02_to_wgs84
def gd_convert_lbs_location(ak,imei,bts,**kwargs):
    """
    bts:
        1. ( mcc,mnc,lac,cellid,signal)
        2.
        [
          [mcc,mnc,lac,cellid,signal],
            ..
         ]

    return:
        {"infocode":"10000",
            "result":{"city":"惠州市","province":"广东省",
            "poi":"惠州会展中心","adcode":"441302","street":"文昌一路",
            "desc":"广东省 惠州市 惠城区 惠州大道 靠近惠州会展中心",
            "country":"中国","type":"4","location":"114.4209817,23.1027075",
            "road":"惠州大道","radius":"550","citycode":"0752"},
        "info":"OK","status":"1"}
    """
    debug = kwargs.get('debug')
    url = "http://apilocate.amap.com/position?accesstype=0&imei={imei}&cdma=0&bts={bts}&output=json&key={key}"
    main = ''
    nears =[]
    if not isinstance(bts[0],(list,tuple)):
        bts = map(lambda _:str(_),bts)
        main = ','.join(bts)
    else:
        bts[0] = map(lambda _:str(_),bts[0])
        main = ','.join(bts[0])
        remains = bts[1:]
        for p in remains:
            p = map(lambda _: str(_), p)
            nears.append(','.join(p))
    nearbts = '|'.join(nears)

    url = url.format(imei=imei,bts=main,key = ak)
    if nearbts:
        url = url +'&nearbts='+nearbts

    if debug:
        debug('gd_convert_lbs_location: {}'.format(url) )  #  调试输出

    r = requests.get(url)
    result = r.json().get('result',{})
    data = {}
    lon,lat = result['location'].split(',')

    data['lon'] = float(lon)
    data['lat'] = float(lat)
    data['radius'] = float(result.get('radius',0))
    data['address'] =result.get('country','') + result.get('province','')+ \
                     result.get('city','')+result.get('street','') + result.get('poi','')
    data['desc'] = result.get('desc','')

    data['lon'],data['lat'] = gcj02_to_wgs84(data['lon'],data['lat'])

    if debug:
        debug('gd_convert_lbs_location: data {}'.format(str(data)) )
    return data


"""
https://restapi.amap.com/v3/geocode/regeo?output=json&location=121.2,31.22&key=c0c74a14f8b411cc5433e8946bf82377&radius=1000&extensions=base
refs: https://lbs.amap.com/api/webservice/guide/api/georegeo/


{
"status": "1",
"regeocode": {
"addressComponent": {
"city": [],
"province": "上海市",
"adcode": "310118",
"district": "青浦区",
"towncode": "310118109000",
"streetNumber": {
"number": "283号",
"location": "121.201901,31.2237219",
"direction": "东北",
"distance": "451.642",
"street": "华志路"
},
"country": "中国",
"township": "重固镇",
"businessAreas": [
[]
],
"building": {
"name": [],
"type": []
},
"neighborhood": {
"name": [],
"type": []
},
"citycode": "021"
},
"formatted_address": "上海市青浦区重固镇中淮路"
},
"info": "OK",
"infocode": "10000"
}

"""

def gd_geocoding_address( ak,lon, lat,radius=1000):
    url ='https://restapi.amap.com/v3/geocode/regeo?output=json&location={lon},{lat}&key={key}&radius={radius}&extensions=base'
    try:
        url = url.format(lon=lon,lat=lat,key=ak,radius=radius)
        resp = requests.get(url)
        data = resp.json().get('result', {})
        address = data.get('formatted_address', '')
    except:
        traceback.print_exc()
        # instance.getLogger().error("<%s> geocoding failed!" % (self.name,))
    return address


def gd_convert_wifi_location(ak,imei,macs,**kwargs):
    """
    macs:
        1. ( mac,signal)

    """
    debug = kwargs.get('debug')

    url = "http://apilocate.amap.com/position?accesstype=1&imei={imei}&macs={macs}&output=json&key={key}"
    main = ''
    nears =[]

    macs = map(lambda mac:'{},{}'.format(str(mac[0]),str(mac[0])),macs)
    macs = '|'.join(macs)


    url = url.format(imei=imei,bts=main,key = ak,macs = macs)

    if debug:
        debug('gd_convert_wifi_location: {}'.format(url) )

    r = requests.get(url)
    result = r.json().get('result',{})
    data = {}
    if int(result.get('type')) == 0:
        if debug:
            debug('wifi location failed. {}'.format(result))
        return data
    lon,lat = result['location'].split(',')

    data['lon'] = float(lon)
    data['lat'] = float(lat)
    data['radius'] = float(result.get('radius',0))
    data['address'] =result.get('country','') + result.get('province','')+ \
                     result.get('city','')+result.get('street','') + result.get('poi','')
    data['desc'] = result.get('desc','')

    data['lon'],data['lat'] = gcj02_to_wgs84(data['lon'],data['lat'])
    if debug:
        debug('gd_convert_wifi_location: data {}'.format(str(data)) )
    return data
