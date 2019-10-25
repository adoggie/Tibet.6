# coding:utf-8

# CommandChannelTradeAdapterGet   = 'trade.command.channel.adapters.{account}.read' # 交易适配器接收通道
# CommandChannelTradeAdapterWRITE  = 'trade.command.channel.adapters.{account}.write'   # 策略运行器接收通道 （广播接收)

#服务程序的命令接收和发送消息的通道地址
ServiceCommandChannelAddressGet = 'redis/trade.command.channel.{service_type}.{service_id}.get/queue'
ServiceCommandChannelAddressSub = 'redis/trade.command.channel.{service_type}.{service_id}.sub/pubsub'

ServiceCommandChannelAddressPut = 'redis/trade.command.channel.{service_type}.{service_id}.put/queue'
ServiceCommandChannelAddressPub = 'redis/trade.command.channel.{service_type}.{service_id}.pub/pubsub'


CommandChannelTradeAdapterLauncherSub = 'redis/trade.command.channel.adapter.launcher.sub/pubsub'  # 适配器加载器的消息接收通道

TradeAdapterServiceIdFormat = '{product}.{account}' # 交易适配器服务ID的命名格式

ServiceKeepAlivedTime = 5   # 指定时间内必须保活，否则视为离线

DevelopAccountNameFormat    = "development.accounts.{product}.{account}"
TradeAccountNameFormat      = "trade.accounts.{product}.{account}"
DevelopUserAccountQuotaFormat = "development.users.{user}.quotas.{account}"
TradeUserAccountQuotaFormat = "trade.users.{user}.quotas.{account}"

TradeAvailableServiceTypeFormat = "trade.available.{}"
TradeAvailableServiceFullNameFormat = "trade.available.{}.{}"
TradeAvailableServiceLockFormat = "trade.available.lock.{}.{}"

DevelopUserStrategyKeyPrefix ='development.users.{user}.strategies.{strategy_name}'
TradeUserStrategyKeyPrefix = 'trade.users.{user}.strategies.{strategy_name}'

CTAContractListKey = 'cta_contract_list'
XtpContractListKey = 'xtp_contract_list'
CtpDepthMarketDataListKey = 'ctp_depth_market_data_list'

CTAContractCommissionListKey = 'cta_contract_commission_list'  # 合约手续费定义
CtpMarketSymbolTickFormat = 'ctp_market_symbol_tick_{symbol}'  # 期货合约的最新市场报价
XtpMarketSymbolTickFormat = 'xtp_market_symbol_tick_{symbol}'  # 期货合约的最新市场报价
CoinMarketSymbolTickFormat = 'coin_market_symbol_tick_{symbol}'  # 期货合约的最新市场报价

TradeRequestId_StrategyId_HashFormat = 'trade.request_ids.{product}.{account}' #存放的所有交易账户发生的交易发单序列，用于跟策略关联
TradeRequestId_Current_Format = 'trade.request_id.current.{product}.{account}' #当前最大发单请求编号

CtpMarket_RequestId_Format = 'trade.ctp.market.request_id.current'

TradeLog_Ctp_DBName = 'TradeLog_Ctp_{account}'

class StrategyRunMode(object):
    Null        = 'null'
    Development = 'dev'
    Product     = 'product'
