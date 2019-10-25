
选股公式

通达信函数参考:
https://www.cnblogs.com/ftrako/p/4011171.html


筛选振幅股票

    ZF:=100*(H-L)/REF(C,1);
    XG:ZF>=(1+N*0.001)*REF(ZF,1);
    
    把n设成参数,默认为30,就表示3％