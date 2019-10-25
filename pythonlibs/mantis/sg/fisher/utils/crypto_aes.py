from Crypto.Cipher import AES
import os

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]

key = os.urandom(16)  # the length can be (16, 24, 32)
# key='xxxxx'#32位或者0-f的数值，对应16字节
text = 'content==顶你哦，记得回访哦xxxxx'

# def encrypt(data,secret)
cipher = AES.new(key, AES.MODE_ECB)  # ECB模式

encrypted = cipher.encrypt(pad(text)).encode('hex')
print encrypted  # will be something like 'f456a6b0e54e35f2711a9fa078a76d16'

decrypted = unpad(cipher.decrypt(encrypted.decode('hex')))
print decrypted