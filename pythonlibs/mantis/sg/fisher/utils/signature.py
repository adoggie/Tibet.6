#coding:utf-8

import hashlib
import urllib
import time
from urlparse import urljoin

def make_signature(secret_key,params,base_url=''):
    """
    创建数据签名
    upper(md5(secret_key+params+secret_key))

    :param secret_key:
    :param params:
    :return:

    ('1673A85BF60AE543F15688B195C8738C',
    'http://test.com:9999/redirect?timestamp=1494602244&app_id=test&sign=1673A85BF60AE543F15688B195C8738C')
    """
    keys = params.keys()
    keys = sorted(keys)
    data = ''.join(map(lambda x: "%s%s" % (x, params[x]), keys))
    data = '%s%s%s' % (secret_key, data, secret_key)

    md = hashlib.md5()
    md.update( data )
    sign = md.hexdigest().upper()
    data =params
    data['sign'] = sign
    suffix = urllib.urlencode(data)
    if base_url:
        base_url+='?'
    url = base_url+suffix

    url = urljoin(url,'')
    return sign,url

if __name__ == '__main__':
    app_id = 'test'
    secret_key = 'zhangbin'
    timestamp = int(time.time())
    redirect_url = 'http://test.com:9999/redirect'
    print timestamp
    print make_signature(secret_key,{'app_id':app_id,
        'user_id':'zhouxin',
        'timestamp':timestamp},
        'http://test.com:9999/redirect')