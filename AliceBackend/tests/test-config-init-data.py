# coding: utf-8

d = '78 78 3B 28 10 01 0D 02 02 02 01 CC 00 28 7D 00 1F 71 3E 28 7D 00 1F 72 31 28 7D 00 1E 23 2D 28 7D 00 1F 40 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF 00 02 00 05 B1 4B 0D 0A'

print ''.join(map(chr,map(lambda _:int(_,16),d.split())))