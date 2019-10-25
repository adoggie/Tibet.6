#coding:utf-8
import json
from Crypto.Cipher import AES
import os
import binascii
import hashlib
from Crypto import Random
import base64

def aes_encode_ecb(params, key='1' * 16):
    """
    aes 加密 ECB/128/PAD5
    params: ( string or dict )  dict类型转换为json字符串再进行加密
    key : 16 字节长度的秘钥
    """
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    text = params
    if isinstance(text, dict):
        text = json.dumps(params)
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(text))
    return ciphertext
    # return  base64.b64encode(ciphertext)

def aes_decode_ecb(data,key):
    """
    aes 解密
    data : 加密数据
    key : 16字节长度的解密秘钥
    """
    unpad = lambda s: s[0:-ord(s[-1])]
    cipher = AES.new(key, AES.MODE_ECB)  # ECB模式
    decrypted = unpad(cipher.decrypt(data))
    return decrypted

keyhex = '51aff7101e4e84314610b7f04af4a68c'
app_id = "324e22b92897f000"


def make_signature(secret_key, params):
    """
    创建数据签名
    sign = hex(sha1(sorted(keys_of_params)+secret_key))
    params={"k1":"v1","k2":"v2"}
    secrect = 'abc'
    data = 'k1v1k2v2abc'
    sign = upper(sha1(data))  # sign-> F18FDACDD55992AD76E04FF7023F020466D3BF81
    """

    keys = params.keys()
    keys = sorted(keys)
    data = ''.join(map(lambda x: "%s%s" % (x, params[x]), keys))
    # data = ''.join(map(lambda x: "%s" % ( params[x]), keys))
    print keys , secret_key
    data = '%s%s' % (data, secret_key)
    sha1 = hashlib.sha1()
    sha1.update(data)
    sign = sha1.hexdigest()

    return sign



def make_signature_for_green(secret_key, params):
    """
    创建数据签名(绿城规格的签名方式，仅对value拼接)
    sign = hex(sha1(sorted(values_of_params+secret_key)))

    params={"k1":"v1","k2":"v2"}
    secrect = 'abc'
    data = 'v1v2abc'
    sign = sha1(data)

    """
    values = params.values()
    values.append(secret_key)
    values = sorted(values)
    # data = ''.join(map(lambda x: "%s%s" % (x, params[x]), keys))
    data = ''.join(map(lambda x: "%s" % x, values))
    # print keys , secret_key
    # data = '%s%s' % (data, secret_key)
    sha1 = hashlib.sha1()
    sha1.update(data)
    sign = sha1.hexdigest()

    return sign


sample=""" {"signature":"3c21a3760582846b253a935980c287a1d6387510","nonce":"lUxPFBRDsuZn","app_id":"324e22b92897f000","content":"45xdo0ji0EEUGpDz36xP1BiA/BK9ICcF6B2YXwofRPJyVsLqafF7W8KVK35pjd6WRjwB2Bnay9Yxty0NN9yri7OEAkE9Hk/gEv3+r9SnkCIdFOh+7OceBKIJ/U7S7wnsl3lczd0K8IZ8Iae7w7pTtDQdW3XGph55qjyZuRYWND309yRXxEFDIu/R2/RNsAjSFk0HajqcYvcaZGOU3J4iGfSzkqp0kEMg0Hx8VagfqLh5r+8k3vKIATlMYXf2hzO7WF7NSayP8wOmBo0LsLTujvGdeOYulF8wUpR/hQueznGIktmhcq+gYYpFKEApm0zQ","timestamp":"1561002676035"}"""

def sign_check_and_get_data(jsondata,keyhex=keyhex,signature='signature' , content='content'):
    """
    检查签名是否正确，并解密 content 项数据
    :param jsondata:  string or dict ,  数据对象必须包含key: 'signature' , 'content'
            'content' 内容 aes 128 加密
    :param keyhex:      hex(key) 32字节
    :param signature:   签名字段名
    :param content:     加密内容字段名
    :return:
        {signature:'',content:'',...}
        {} if sign error .

    examples:
        data = {"signature":"3c21a3760582846b253a935980c287a1d6387510","nonce":"lUxPFBRDsuZn","app_id":"324e22b92897f000","content":"45xdo0ji0EEUGpDz36xP1BiA","timestamp":"1561002676035"}

        sign_check_and_get_data( data  , '51aff7101e4e84314610b7f04af4a68c')

    """
    params = {}
    if isinstance(jsondata,(str,unicode)):
        params = json.loads(jsondata)
    else:
        params.update(jsondata)
    sign = params[signature]
    if params.has_key(signature):
        del params[signature]

    finger = make_signature_for_green(keyhex, params)
    if sign != finger: # invalid signature
        print 'signature error'
        return {}
    key = binascii.a2b_hex(keyhex)
    params[content] = base64.b64decode( params[content])
    origin_text = aes_decode_ecb(params[content],key)
    params[content] = origin_text
    return params

def sign_data(datadict,keyhex=keyhex,signature='signature' , content='content'):
    """
    数据加密并签名 base64(aes(datadict['content']))
    :param datadict:  [in] 待签名字典对象 , 属性 content 类型: str or dict ,  { content:'',.. }
    :param keyhex:   [in]  32位长度的秘钥（hex）
    :param signature: [out]
    :param content: [out]
    :return:
        dict { signature:'', content: base64(aes(datadict['content'])) ,..}

    examples:
        data = {"nonce":"lUxPFBRDsuZn","app_id":"324e22b92897f000","content":"45xdo0ji0EEUGpDz36xP1BiA","timestamp":"1561002676035"}

        sign_data( data , '51aff7101e4e84314610b7f04af4a68c')
    """
    params = {}
    params.update(datadict)
    key = binascii.a2b_hex(keyhex)
    params[content] = base64.b64encode( aes_encode_ecb(params[content],key) )
    sign = make_signature_for_green(keyhex,params)
    params[signature] = sign
    return params



def test():
    params = json.loads(sample)
    content = params.get('content')
    text = aes_decode_ecb(base64.b64decode(content), key)
    print text
    del params['signature']
    print make_signature_for_green(keyhex,params)

# print sign_check_and_get_data(sample,keyhex)
# print sign_data(dict(content='abcedfg'),keyhex)
#
key =binascii.a2b_hex(keyhex) # 32 hexlify -> 16 raw bytes
message = 'hello'
ciphertext = aes_encode_ecb(message,key)
text = aes_decode_ecb(ciphertext,key)
print text

if __name__ == '__main__':
    # test()
    pass