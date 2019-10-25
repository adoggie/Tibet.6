from base import *
from strategy import *
from product import *
from market import *
from trader import *
from controller import *
from tradeobject import *
from position import  *
from logger import *
# from futures import *
import futures

def init_default():
    controller.registerProduct(FuturesProduct())
    controller.registerProduct(StocksProduct())

controller = TradeController()
init_default()

stocks = controller.stocks
# Futures = controller.futures

println = controller.getLogger().info
print_line = println

