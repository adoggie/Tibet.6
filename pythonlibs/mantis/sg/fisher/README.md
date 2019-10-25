
Fisher
====
本地交易程序框架



## Problems

1. 获取持仓信息的得到空列表
    
     pos_list = self.ctx.Strategy.Product.All_Pos
        print pos_list
        

## AMS 系统问题
1. 程序使用mongodb，申请线程，由于异常导致策略被ams容器终止，多次出现，会令ams系统崩溃，提示内存不足的问题
2. 接收k线时发现时钟滞后4-5秒