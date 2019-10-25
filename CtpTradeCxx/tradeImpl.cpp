//
// Created by scott on 2019/5/21.
//

#include "trade.h"
#include "app.h"
#include <jsoncpp/json/json.h>
#include <boost/algorithm/string.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/lexical_cast.hpp>
#include <thread>
#include <sstream>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/lexical_cast.hpp>
#include <algorithm>
#include "tradeImpl.h"

//#include <chrono>

#include "http.h"

#define SCOPE_LOCK std::lock_guard<std::recursive_mutex> lock(rmutex_);

ConnectionOptions connection_options;
Redis * redis_;
std::string pubchan_event_name_;


//scott
void TdApi::processFrontDisconnected(Task task)
{
//    PyLock lock;
//    this->onFrontDisconnected(task.task_id);
    Application::instance()->getLogger().debug("Front Server Disconnected.");
};

//scott
void TdApi::processHeartBeatWarning(Task task)
{
//    PyLock lock;
//    this->onHeartBeatWarning(task.task_id);
};


//#include <locale>
//#include <codecvt>
//
//std::string gb2312_to_utf8(std::string const &strGb2312)
//{
//    std::vector<wchar_t> buff(strGb2312.size());
//#ifdef _MSC_VER
//    std::locale loc("zh-CN");
//#else
//    std::locale loc("zh_CN.GB18030");
//#endif
//    wchar_t* pwszNext = nullptr;
//    const char* pszNext = nullptr;
//    mbstate_t state = {};
//    int res = std::use_facet<std::codecvt<wchar_t, char, mbstate_t> >
//            (loc).in(state,
//                     strGb2312.data(), strGb2312.data() + strGb2312.size(), pszNext,
//                     buff.data(), buff.data() + buff.size(), pwszNext);
//
//    if (std::codecvt_base::ok == res)
//    {
//        std::wstring_convert<std::codecvt_utf8<wchar_t>> cutf8;
//        return cutf8.to_bytes(std::wstring(buff.data(), pwszNext));
//    }
//
//    return "";
//
//}

//mark
// 响应用户登录时间 scott
void TdApi::processRspUserLogin(Task task)
{
    CThostFtdcRspUserLoginField task_data = any_cast<CThostFtdcRspUserLoginField>(task.task_data);
//
    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);

    if(task_error.ErrorID == 0){ //登录成功
        logined_ = true;
        front_id_ = 0;
        front_id_ = (int)task_data.FrontID;
        session_id_ = (int)task_data.SessionID;
        std::string value ;
        value = task_data.MaxOrderRef;
        boost::trim(value);
        order_ref_ = boost::lexical_cast<int>(value) ;
        ftd_login_field_ = task_data;
//        boost::trim()

//        dict req;
//        req['BrokerID'] = broker_id_
//        req['InvestorID'] = user_id_;
        CThostFtdcSettlementInfoConfirmField req;
        memset(&req,0,sizeof(req));
        StrValueAssign(broker_id_, req.BrokerID);
        StrValueAssign(user_id_ , req.InvestorID);
        Application::instance()->getLogger().debug("broker:"+ broker_id_ + " user_id:"+user_id_);
        int ret = this->api->ReqSettlementInfoConfirm(&req, nextRequestId());

        std::stringstream ss;
        ss<<"User Login Okay . ReqSettlementInfoConfirm CallRetCode:" << ret ;
        Application::instance()->getLogger().debug(ss.str() );

        std::this_thread::sleep_for(std::chrono::seconds(1));
        queryOrder(); //
        std::this_thread::sleep_for(std::chrono::seconds(1));
        queryTrade();
    }else{
        logined_ = false;
        Application::instance()->getLogger().error("Login Failed.");
    }
};

//scott 用户登出
void TdApi::processRspUserLogout(Task task)
{
//    PyLock lock;
//    CThostFtdcUserLogoutField task_data = any_cast<CThostFtdcUserLogoutField>(task.task_data);
//    dict data;
//    data["UserID"] = task_data.UserID;
//    data["BrokerID"] = task_data.BrokerID;
//
//    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspUserLogout(data, error, task.task_id, task.task_last);

    logined_ = false;
    authed_ = false;
};


// scott 确认结算信息回报
void TdApi::processRspSettlementInfoConfirm(Task task)
{
    Application::instance()->getLogger().debug("processRspSettlementInfoConfirm()..");
};


// scott 查询合约保证金
void TdApi::processRspQryInstrumentMarginRate(Task task)
{
//    PyLock lock;
    CThostFtdcInstrumentMarginRateField task_data = any_cast<CThostFtdcInstrumentMarginRateField>(task.task_data);
    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    this->onRspQryInstrumentMarginRate(data, error, task.task_id, task.task_last);

    margin_rates_[ task_data.InstrumentID] = task_data;
    Application::instance()->getLogger().debug("processRspQryInstrumentMarginRate().. , Instrument:" + std::string(task_data.InstrumentID));

};


// scott 结算查询返回
void TdApi::processRspQrySettlementInfo(Task task)
{
//    PyLock lock;
    CThostFtdcSettlementInfoField task_data = any_cast<CThostFtdcSettlementInfoField>(task.task_data);
//    dict data;
//    data["SettlementID"] = task_data.SettlementID;
//    data["InvestorID"] = task_data.InvestorID;
//    data["SequenceNo"] = task_data.SequenceNo;
//    data["Content"] = task_data.Content;
//    data["TradingDay"] = task_data.TradingDay;
//    data["BrokerID"] = task_data.BrokerID;
//
//    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspQrySettlementInfo(data, error, task.task_id, task.task_last);
    Application::instance()->getLogger().debug( "processRspQrySettlementInfo() ..");
};

// scott
void TdApi::processRspError(Task task)
{
//    PyLock lock;
    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspError(error, task.task_id, task.task_last);
    Application::instance()->getLogger().error("onRspError");
};

void TdApi::scheduleQuery(){
    int query_interval;
    Config & cfg = Application::instance()->getConfig();
    query_interval = cfg.get_int("query_interval",1) ;
    if( !query_timer_) {
        query_timer_ = std::make_shared<boost::asio::deadline_timer >(Application::instance()->io_service(),
                                                boost::posix_time::seconds(query_interval));
    }
    query_timer_->async_wait(std::bind(&TdApi::query_work_timer, this));

}


//void TdApi::scheduleQuery(){
//    return;
//    Config & cfg = Application::instance()->getConfig();
//    int query_interval = cfg.get_int("query_interval",1) ;
//    //        query_timer_->expires_from_now(boost::posix_time::seconds(query_interval));
//    while(true) {
//        std::this_thread::sleep_for(std::chrono::seconds(query_interval));
//        Application::instance()->getLogger().debug("query_work_timer()..");
//        if (!logined_) {
//            continue;
//        }
//
//        auto head = query_functions_.begin();
//        if (head != query_functions_.end()) {
//            auto &fx = *head;
//            fx();
//            query_functions_.erase(head);
//            query_functions_.push_back(fx);
//
//        }
//    }
//}

void TdApi::query_work_timer(){
    Config & cfg = Application::instance()->getConfig();
    int query_interval = cfg.get_int("query_interval",1) ;

    std::lock_guard<std::mutex> lock(mutex_query_);

    query_timer_->expires_from_now(boost::posix_time::seconds(query_interval));

//    Application::instance()->getLogger().debug("query_work_timer()..");
    if( !logined_){
        scheduleQuery();
        return ;
    }

    auto head = query_functions_.begin();
    if( head != query_functions_.end()){
        auto fx = *head;
        fx();
        std::this_thread::sleep_for(std::chrono::seconds(1));
        query_functions_.erase(head);
        query_functions_.push_back(fx);
        std::stringstream ss;
        ss << "function size:" << query_functions_.size();
        Application::instance()->getLogger().debug(ss.str());
    }
    scheduleQuery();
}

void TdApi::login(){
    if( logined_){
        return;
    }
//    dict req;
//    req['UserID'] = user_id_;
//    req['Password'] = password_;
//    req['BrokerID'] = broker_id_;
//
//    reqUserLogin(req, nextRequestId());

    CThostFtdcReqUserLoginField myreq = CThostFtdcReqUserLoginField();
    memset(&myreq, 0, sizeof(myreq));
//    getStr(req, "MacAddress", myreq.MacAddress);
//    getStr(req, "UserProductInfo", myreq.UserProductInfo);
//    getStr(req, "UserID", myreq.UserID);
//    getStr(req, "TradingDay", myreq.TradingDay);
//    getStr(req, "InterfaceProductInfo", myreq.InterfaceProductInfo);
//    getStr(req, "BrokerID", myreq.BrokerID);
//    getStr(req, "ClientIPAddress", myreq.ClientIPAddress);
//    getStr(req, "OneTimePassword", myreq.OneTimePassword);
//    getStr(req, "ProtocolInfo", myreq.ProtocolInfo);
//    getStr(req, "Password", myreq.Password);

    user_id_.copy(myreq.UserID,sizeof(myreq.UserID));
    broker_id_.copy(myreq.BrokerID,sizeof(myreq.BrokerID));
    password_.copy(myreq.Password,sizeof(myreq.Password));
    int i = this->api->ReqUserLogin(&myreq, nextRequestId());
}

void TdApi::authenticate(){

//    Config & cfg = Application::instance()->getConfig();
//
//    std::string product, authcode;
//
//    product = cfg.get_string("product_info");
//    authcode = cfg.get_string("auth_code");

//    dict req;
//    req['UserID'] = cfg.get_string("ctp.user_id");
//    req['BrokerID'] = cfg.get_string("ctp.broker_id");
//    req['AuthCode'] = authcode;
//    req['UserProductInfo'] = product;
//
//    reqAuthenticate(req, nextRequestId());

    CThostFtdcReqAuthenticateField myreq = CThostFtdcReqAuthenticateField();
    memset(&myreq, 0, sizeof(myreq));
//    getStr(req, "UserID", myreq.UserID);
//    getStr(req, "AuthCode", myreq.AuthCode);
//    getStr(req, "BrokerID", myreq.BrokerID);
//    getStr(req, "UserProductInfo", myreq.UserProductInfo);

    StrValueAssign( user_id_, myreq.UserID);
    StrValueAssign( auth_code_, myreq.AuthCode);
    StrValueAssign( broker_id_, myreq.BrokerID);
#ifdef _CHUANTOU
    StrValueAssign( product_info_, myreq.AppID);
#endif

    int i = this->api->ReqAuthenticate(&myreq, nextRequestId());
}

//scott
void TdApi::processFrontConnected(Task task)
{
//    PyLock lock;
//    this->onFrontConnected();
    Application::instance()->getLogger().debug("!! -- Front Server Connected. -- !!");

    if( !requireAuthentication_ ){
        // do login
        login();
    }else{
        authenticate();
    }


};

//持仓查询回报
void TdApi::processRspQryInvestorPosition(Task task)
{
    SCOPED_LOCK
//    PyLock lock;
    CThostFtdcInvestorPositionField task_data = any_cast<CThostFtdcInvestorPositionField>(task.task_data);

    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);

//    this->onRspQryInvestorPosition(data, error, task.task_id, task.task_last);
    Application::instance()->getLogger().debug("processRspQryInvestorPosition().." + std::string(task_data.InstrumentID));

//    positions_[ task_data.InstrumentID] = task_data;
    positions_back_.push_back(task_data)  ;
    if( task.task_last){
        positions_ = positions_back_;
    }
//    if(task.task_last){
//        positions_ = positions_tmp_;
//    }
};

//资金余额
void TdApi::processRspQryTradingAccount(Task task)
{
    CThostFtdcTradingAccountField task_data = any_cast<CThostFtdcTradingAccountField>(task.task_data);
    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    this->onRspQryTradingAccount(data, error, task.task_id, task.task_last);
    if(task_error.ErrorID == 0){
        ftd_trade_account_ = task_data;
        Application::instance()->getLogger().debug("processRspQryTradingAccount()..");
    }

};

// 交易手续费查询
void TdApi::processRspQryInstrumentCommissionRate(Task task)
{
//    PyLock lock;
    CThostFtdcInstrumentCommissionRateField task_data = any_cast<CThostFtdcInstrumentCommissionRateField>(task.task_data);
//    dict data;
//    data["InstrumentID"] = task_data.InstrumentID;
//    data["OpenRatioByMoney"] = task_data.OpenRatioByMoney;
//    data["CloseRatioByVolume"] = task_data.CloseRatioByVolume;
//    data["BizType"] = task_data.BizType;
//    data["CloseTodayRatioByMoney"] = task_data.CloseTodayRatioByMoney;
//    data["ExchangeID"] = task_data.ExchangeID;
//    data["InvestorID"] = task_data.InvestorID;
//    data["BrokerID"] = task_data.BrokerID;
//    data["InvestorRange"] = task_data.InvestorRange;
//    data["CloseRatioByMoney"] = task_data.CloseRatioByMoney;
//    data["OpenRatioByVolume"] = task_data.OpenRatioByVolume;
//    data["CloseTodayRatioByVolume"] = task_data.CloseTodayRatioByVolume;

    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspQryInstrumentCommissionRate(data, error, task.task_id, task.task_last);

    commission_rates_[ task_data.InstrumentID] = task_data;

    std::stringstream ss;
    ss << "processRspQryInstrumentCommissionRate() , instrument:" << task_data.InstrumentID;
    Application::instance()->getLogger().debug( ss.str());
};


// 查询合约信息
void TdApi::processRspQryInstrument(Task task)
{
//    PyLock lock;
    CThostFtdcInstrumentField task_data = any_cast<CThostFtdcInstrumentField>(task.task_data);
//    dict data;
//    data["IsTrading"] = task_data.IsTrading;
//    data["ExpireDate"] = task_data.ExpireDate;
//    data["PositionDateType"] = task_data.PositionDateType;
//    data["LongMarginRatio"] = task_data.LongMarginRatio;
//    data["StrikePrice"] = task_data.StrikePrice;
//    data["UnderlyingMultiple"] = task_data.UnderlyingMultiple;
//    data["PositionType"] = task_data.PositionType;
//    data["ProductClass"] = task_data.ProductClass;
//    data["MinSellVolume"] = task_data.MinSellVolume;
//    data["InstrumentName"] = task_data.InstrumentName;
//    data["ShortMarginRatio"] = task_data.ShortMarginRatio;
//    data["VolumeMultiple"] = task_data.VolumeMultiple;
//    data["MaxMarginSideAlgorithm"] = task_data.MaxMarginSideAlgorithm;
//    data["DeliveryYear"] = task_data.DeliveryYear;
//    data["CombinationType"] = task_data.CombinationType;
//    data["CreateDate"] = task_data.CreateDate;
//    data["InstrumentID"] = task_data.InstrumentID;
//    data["MaxLimitOrderVolume"] = task_data.MaxLimitOrderVolume;
//    data["ExchangeID"] = task_data.ExchangeID;
//    data["MinLimitOrderVolume"] = task_data.MinLimitOrderVolume;
//    data["MaxMarketOrderVolume"] = task_data.MaxMarketOrderVolume;
//    data["OptionsType"] = task_data.OptionsType;
//    data["StartDelivDate"] = task_data.StartDelivDate;
//    data["DeliveryMonth"] = task_data.DeliveryMonth;
//    data["InstrumentCode"] = task_data.InstrumentCode;
//    data["MinBuyVolume"] = task_data.MinBuyVolume;
//    data["PriceTick"] = task_data.PriceTick;
//    data["InstLifePhase"] = task_data.InstLifePhase;
//    data["ExchangeInstID"] = task_data.ExchangeInstID;
//    data["MinMarketOrderVolume"] = task_data.MinMarketOrderVolume;
//    data["EndDelivDate"] = task_data.EndDelivDate;
//    data["UnderlyingInstrID"] = task_data.UnderlyingInstrID;
//    data["OpenDate"] = task_data.OpenDate;
//    data["ProductID"] = task_data.ProductID;

    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspQryInstrument(data, error, task.task_id, task.task_last);
    instruments_[ std::string(task_data.InstrumentID) ] = task_data;
};


//查询深度行情
void TdApi::processRspQryDepthMarketData(Task task)
{

//    PyLock lock;
    CThostFtdcDepthMarketDataField task_data = any_cast<CThostFtdcDepthMarketDataField>(task.task_data);
//    dict data;
//    data["HighestPrice"] = task_data.HighestPrice;
//    data["BidPrice5"] = task_data.BidPrice5;
//    data["BidPrice4"] = task_data.BidPrice4;
//    data["BidPrice1"] = task_data.BidPrice1;
//    data["BidPrice3"] = task_data.BidPrice3;
//    data["BidPrice2"] = task_data.BidPrice2;
//    data["LowerLimitPrice"] = task_data.LowerLimitPrice;
//    data["OpenPrice"] = task_data.OpenPrice;
//    data["AskPrice5"] = task_data.AskPrice5;
//    data["AskPrice4"] = task_data.AskPrice4;
//    data["AskPrice3"] = task_data.AskPrice3;
//    data["PreClosePrice"] = task_data.PreClosePrice;
//    data["AskPrice1"] = task_data.AskPrice1;
//    data["PreSettlementPrice"] = task_data.PreSettlementPrice;
//    data["AskVolume1"] = task_data.AskVolume1;
//    data["UpdateTime"] = task_data.UpdateTime;
//    data["UpdateMillisec"] = task_data.UpdateMillisec;
//    data["AveragePrice"] = task_data.AveragePrice;
//    data["BidVolume5"] = task_data.BidVolume5;
//    data["BidVolume4"] = task_data.BidVolume4;
//    data["BidVolume3"] = task_data.BidVolume3;
//    data["BidVolume2"] = task_data.BidVolume2;
//    data["PreOpenInterest"] = task_data.PreOpenInterest;
//    data["AskPrice2"] = task_data.AskPrice2;
//    data["Volume"] = task_data.Volume;
//    data["AskVolume3"] = task_data.AskVolume3;
//    data["AskVolume2"] = task_data.AskVolume2;
//    data["AskVolume5"] = task_data.AskVolume5;
//    data["AskVolume4"] = task_data.AskVolume4;
//    data["UpperLimitPrice"] = task_data.UpperLimitPrice;
//    data["BidVolume1"] = task_data.BidVolume1;
//    data["InstrumentID"] = task_data.InstrumentID;
//    data["ClosePrice"] = task_data.ClosePrice;
//    data["ExchangeID"] = task_data.ExchangeID;
//    data["TradingDay"] = task_data.TradingDay;
//    data["PreDelta"] = task_data.PreDelta;
//    data["OpenInterest"] = task_data.OpenInterest;
//    data["CurrDelta"] = task_data.CurrDelta;
//    data["Turnover"] = task_data.Turnover;
//    data["LastPrice"] = task_data.LastPrice;
//    data["SettlementPrice"] = task_data.SettlementPrice;
//    data["ExchangeInstID"] = task_data.ExchangeInstID;
//    data["LowestPrice"] = task_data.LowestPrice;
//    data["ActionDay"] = task_data.ActionDay;

    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspQryDepthMarketData(data, error, task.task_id, task.task_last);
    market_datas_[task_data.InstrumentID] = task_data;

};

//撤单响应（柜台） 此刻未到交易所
void TdApi::processRspOrderAction(Task task)
{
//    PyLock lock;
    CThostFtdcInputOrderActionField task_data = any_cast<CThostFtdcInputOrderActionField>(task.task_data);
//    dict data;
//    data["InstrumentID"] = task_data.InstrumentID;
//    data["ExchangeID"] = task_data.ExchangeID;
//    data["ActionFlag"] = task_data.ActionFlag;
//    data["OrderActionRef"] = task_data.OrderActionRef;
//    data["UserID"] = task_data.UserID;
//    data["LimitPrice"] = task_data.LimitPrice;
//    data["OrderRef"] = task_data.OrderRef;
//    data["InvestorID"] = task_data.InvestorID;
//    data["SessionID"] = task_data.SessionID;
//    data["VolumeChange"] = task_data.VolumeChange;
//    data["BrokerID"] = task_data.BrokerID;
//    data["RequestID"] = task_data.RequestID;
//    data["OrderSysID"] = task_data.OrderSysID;
//    data["FrontID"] = task_data.FrontID;

    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspOrderAction(data, error, task.task_id, task.task_last);
    std::stringstream ss ;
    ss << task_data.InstrumentID << " OrderSysId :" << task_data.OrderSysID;
    Application::instance()->getLogger().debug("Exchange Core Recieved Order Request : " + ss.str() );

};

//委托单响应
// 无需关心委托是否回报处于哪个状态，通过定时查询委托单即可知道
void TdApi::processRtnOrder(Task task)
{
    SCOPED_LOCK
    CThostFtdcOrderField task_data = any_cast<CThostFtdcOrderField>(task.task_data);

//
//    this->onRtnOrder(data);

    std::string id;
//    std::sstream ss;
//    id = boost::lexical_cast<std::string>(task_data.FrontID)+"."+ boost::lexical_cast<std::string>(task_data.SessionID) + "." + std::string(task_data.OrderRef);
    id = std::string(task_data.OrderRef);

//    orders_[id] = task_data;

    std::stringstream ss;
    ss << task_data.InstrumentID << task_data.ExchangeID << "." << task_data.OrderSysID;
    orders_[ss.str()] = task_data;


    Json::Value node;
    CThostFtdcOrderField& order = task_data;
    node["event"] = "event_order";

    node["InstrumentID"] = order.InstrumentID;
    node["OrderRef"] = order.OrderRef;
    node["UserID"] = order.UserID;
    node["OrderPriceType"] = order.OrderPriceType;
    node["Direction"] = std::string(1,order.Direction);
    node["CombOffsetFlag"] = order.CombOffsetFlag;
    node["CombHedgeFlag"] = order.CombHedgeFlag;
    node["LimitPrice"] = order.LimitPrice;
    node["VolumeTotalOriginal"] = order.VolumeTotalOriginal;
    node["TimeCondition"] = std::string(1,order.TimeCondition);
    node["GTDDate"] = order.GTDDate;
    node["VolumeCondition"] = std::string(1,order.VolumeCondition);
    node["MinVolume"] = order.MinVolume;
    node["ContingentCondition"] = order.ContingentCondition;
    node["StopPrice"] = order.StopPrice;
    node["ForceCloseReason"] = std::string(1,order.ForceCloseReason);
    node["IsAutoSuspend"] = order.IsAutoSuspend;
    node["RequestID"] = order.RequestID;
    node["OrderLocalID"] = order.OrderLocalID;
    node["ExchangeID"] = order.ExchangeID;
    node["ClientID"] = order.ClientID;
    node["OrderSubmitStatus"] = order.OrderSubmitStatus;
    node["NotifySequence"] = order.NotifySequence;
    node["TradingDay"] = order.TradingDay;
    node["SettlementID"] = order.SettlementID;
    node["OrderSysID"] = order.OrderSysID;
    node["OrderSource"] = order.OrderSource;
    node["OrderStatus"] = order.OrderStatus;
    node["OrderType"] = order.OrderType;
    node["VolumeTraded"] = order.VolumeTraded;
    node["VolumeTotal"] = order.VolumeTotal;
    node["InsertDate"] = order.InsertDate;
    node["InsertTime"] = order.InsertTime;
    node["ActiveTime"] = order.ActiveTime;
    node["SuspendTime"] = order.SuspendTime;
    node["UpdateTime"] = order.UpdateTime;
    node["CancelTime"] = order.CancelTime;
    node["SequenceNo"] = order.SequenceNo;
    node["FrontID"] = order.FrontID;
    node["SessionID"] = order.SessionID;
    node["UserProductInfo"] = order.UserProductInfo;
//    node["StatusMsg"] = order.StatusMsg;
    node["UserForceClose"] = order.UserForceClose;
    node["BrokerOrderSeq"] = order.BrokerOrderSeq;
    node["BranchID"] = order.BranchID;
    std::string json_text = node.toStyledString();
    redis_->publish(pubchan_event_name_, json_text);
    Application::instance()->getLogger().debug("<< Order Return..");
};

//委托单失败
void TdApi::processErrRtnOrderInsert(Task task)
{
//    PyLock lock;
    CThostFtdcInputOrderField task_data = any_cast<CThostFtdcInputOrderField>(task.task_data);

    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;

//    this->onErrRtnOrderInsert(data, error);
    if( task_error.ErrorID){
        this->onQueryResult("processErrRtnOrderInsert",(int)task_error.ErrorID,"");
    }
};

//撤单错误回报
void TdApi::processErrRtnOrderAction(Task task)
{
//    PyLock lock;
    CThostFtdcOrderActionField task_data = any_cast<CThostFtdcOrderActionField>(task.task_data);

    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;

//    this->onErrRtnOrderAction(data, error);
    if( task_error.ErrorID){
        this->onQueryResult("processErrRtnOrderAction",(int)task_error.ErrorID,"");
    }
};

void TdApi::processRtnTrade(Task task)
{
    SCOPED_LOCK
//    PyLock lock;
    CThostFtdcTradeField task_data = any_cast<CThostFtdcTradeField>(task.task_data);
//    dict data;
//    data["TradeType"] = task_data.TradeType;
//    data["TraderID"] = task_data.TraderID;
//    data["HedgeFlag"] = task_data.HedgeFlag;
//    data["TradeTime"] = task_data.TradeTime;
//    data["Direction"] = task_data.Direction;
//    data["ParticipantID"] = task_data.ParticipantID;
//    data["Price"] = task_data.Price;
//    data["ClientID"] = task_data.ClientID;
//    data["Volume"] = task_data.Volume;
//    data["OrderSysID"] = task_data.OrderSysID;
//    data["ClearingPartID"] = task_data.ClearingPartID;
//    data["InstrumentID"] = task_data.InstrumentID;
//    data["ExchangeID"] = task_data.ExchangeID;
//    data["SettlementID"] = task_data.SettlementID;
//    data["UserID"] = task_data.UserID;
//    data["TradingDay"] = task_data.TradingDay;
//    data["BrokerID"] = task_data.BrokerID;
//    data["OffsetFlag"] = task_data.OffsetFlag;
//    data["OrderLocalID"] = task_data.OrderLocalID;
//    data["TradeID"] = task_data.TradeID;
//    data["TradeDate"] = task_data.TradeDate;
//    data["BusinessUnit"] = task_data.BusinessUnit;
//    data["SequenceNo"] = task_data.SequenceNo;
//    data["OrderRef"] = task_data.OrderRef;
//    data["BrokerOrderSeq"] = task_data.BrokerOrderSeq;
//    data["InvestorID"] = task_data.InvestorID;
//    data["ExchangeInstID"] = task_data.ExchangeInstID;
//    data["TradeSource"] = task_data.TradeSource;
//    data["PriceSource"] = task_data.PriceSource;
//    data["TradingRole"] = task_data.TradingRole;
//
//    this->onRtnTrade(data);

//    trades_[ task_data.TradeID ] = task_data;
    Application::instance()->getLogger().debug("<< processRtnTrade() ..");
    trades_.push_back(task_data);

    Json::Value node;
    CThostFtdcTradeField& trade = task_data;
    node["event"] = "event_trade";
    node["InstrumentID"] = trade.InstrumentID;
    node["OrderRef"] = trade.OrderRef;
    node["UserID"] = trade.UserID;
    node["ExchangeID"] = trade.ExchangeID;
    node["TradeID"] = trade.TradeID;
    node["Direction"] = std::string(1,trade.Direction);
    node["OrderSysID"] = trade.OrderSysID;
    node["ParticipantID"] = trade.ParticipantID;
    node["ClientID"] = trade.ClientID;
    node["TradingRole"] = trade.TradingRole;
    node["ExchangeInstID"] = trade.ExchangeInstID;
    node["OffsetFlag"] = trade.OffsetFlag;
    node["HedgeFlag"] = std::string(1, trade.HedgeFlag);
    node["Price"] = trade.Price;
    node["Volume"] = trade.Volume;
    node["TradeDate"] = trade.TradeDate;
    node["TradeTime"] = trade.TradeTime;
    node["TradeType"] = trade.TradeType;
    node["PriceSource"] = trade.PriceSource;
    node["TraderID"] = trade.TraderID;
    node["OrderLocalID"] = trade.OrderLocalID;
    node["ClearingPartID"] = trade.ClearingPartID;
    node["BusinessUnit"] = trade.BusinessUnit;
    node["SequenceNo"] = trade.SequenceNo;
    node["TradingDay"] = trade.TradingDay;
    node["SettlementID"] = trade.SettlementID;
    node["BrokerOrderSeq"] = trade.BrokerOrderSeq;
    node["TradeSource"] = trade.TradeSource;

    std::string json_text = node.toStyledString();
    redis_->publish(pubchan_event_name_, json_text);
    Application::instance()->getLogger().debug("<< Order Return..");


};


void TdApi::processRspOrderInsert(Task task)
{
//    PyLock lock;
    CThostFtdcInputOrderField task_data = any_cast<CThostFtdcInputOrderField>(task.task_data);
//    dict data;
//    data["ContingentCondition"] = task_data.ContingentCondition;
//    data["CombOffsetFlag"] = task_data.CombOffsetFlag;
//    data["UserID"] = task_data.UserID;
//    data["LimitPrice"] = task_data.LimitPrice;
//    data["UserForceClose"] = task_data.UserForceClose;
//    data["Direction"] = task_data.Direction;
//    data["IsSwapOrder"] = task_data.IsSwapOrder;
//    data["VolumeTotalOriginal"] = task_data.VolumeTotalOriginal;
//    data["OrderPriceType"] = task_data.OrderPriceType;
//    data["TimeCondition"] = task_data.TimeCondition;
//    data["IsAutoSuspend"] = task_data.IsAutoSuspend;
//    data["StopPrice"] = task_data.StopPrice;
//    data["InstrumentID"] = task_data.InstrumentID;
//    data["ExchangeID"] = task_data.ExchangeID;
//    data["MinVolume"] = task_data.MinVolume;
//    data["ForceCloseReason"] = task_data.ForceCloseReason;
//    data["BrokerID"] = task_data.BrokerID;
//    data["CombHedgeFlag"] = task_data.CombHedgeFlag;
//    data["GTDDate"] = task_data.GTDDate;
//    data["BusinessUnit"] = task_data.BusinessUnit;
//    data["OrderRef"] = task_data.OrderRef;
//    data["InvestorID"] = task_data.InvestorID;
//    data["VolumeCondition"] = task_data.VolumeCondition;
//    data["RequestID"] = task_data.RequestID;
//
    CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//    dict error;
//    error["ErrorMsg"] = task_error.ErrorMsg;
//    error["ErrorID"] = task_error.ErrorID;
//
//    this->onRspOrderInsert(data, error, task.task_id, task.task_last);
    if( task_error.ErrorID){
        this->onQueryResult("processRspOrderInsert",(int)task_error.ErrorID,"");
    }
};

// 委托查询返回
void TdApi::processRspQryOrder(Task task)
{
    SCOPED_LOCK
//	PyLock lock;
	CThostFtdcOrderField task_data = any_cast<CThostFtdcOrderField>(task.task_data);

//	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	this->onRspQryOrder(data, error, task.task_id, task.task_last);
    std::stringstream ss;
    ss << task_data.InstrumentID << task_data.ExchangeID << "." << task_data.OrderSysID;
    orders_back_[ss.str()] = task_data;
//    orders_back_.push_back(task_data);
    if(task.task_last){
        orders_ = orders_back_;
    }
};

bool TdApi::start(){
    logined_ = false;
    authed_ = false;
//    ConnectionOptions connection_options;
    Config & cfg = Application::instance()->getConfig();

//    connection_options.host = cfg.get_string("redis.host","127.0.0.1");
//    connection_options.port = cfg.get_int("redis.port",6379); 			// The default port is 6379.
////	connection_options.password = "auth";   // Optional. No password by default.
//    connection_options.db = cfg.get_int("redis.db",0);
//    connection_options.socket_timeout = std::chrono::milliseconds(200);

// Connect to Redis server with a single connection.
//    redis_ = new Redis(connection_options);

//	Redis redis1(connection_options);
//	ConnectionPoolOptions pool_options;
//	pool_options.size = 3;  // Pool size, i.e. max number of connections.
// Connect to Redis server with a connection pool.
//	Redis redis2(connection_options, pool_options);
    query_functions_.push_back( std::bind(&TdApi::queryPosition,this));
    query_functions_.push_back( std::bind(&TdApi::queryAccount,this));
//    query_functions_.push_back( std::bind(&TdApi::queryOrder,this));
//    query_functions_.push_back( std::bind(&TdApi::queryTrade,this));

//    std::vector< std::string > instruments;
    std::string text = cfg.get_string("ctp.instruments");
    boost::split(instruments_query_,text,boost::is_any_of(", "));

    connect();

    scheduleQuery();
    return true;
}

void TdApi::stop(){
    this->exit();
//    delete redis_;
}

bool TdApi::connect(){
    Config& cfg = Application::instance()->getConfig();
    user_id_ = cfg.get_string("ctp.user_id");
    broker_id_ = cfg.get_string("ctp.broker_id");
    password_ = cfg.get_string("ctp.password");
    auth_code_ = cfg.get_string("ctp.auth_code");
    product_info_ = cfg.get_string("ctp.product_info");

    std::string conpath = cfg.get_string("ctp.con_path","./cons");
    std::string address = cfg.get_string("ctp.td_addr");

    std::string req_auth ;
    req_auth = cfg.get_string("ctp.require_auth");
    if( req_auth == "true"){
        requireAuthentication_ = true;
    }

    createFtdcTraderApi(conpath);

    subscribePrivateTopic(1);
    subscribePublicTopic(1);

    registerFront(address);
    init();

//    std::this_thread::sleep_for(2s);

//    dict req ;
//    req["UserID"] = cfg.get_string("ctp.user_id");
//    req["Password"] = cfg.get_string("ctp.password");
//    req["BrokerID"] = cfg.get_string("ctp.broker_id");
//    int req_id;
//    req_id = 1;
//    reqUserLogin(req,req_id);
    return true;
}

///请求查询合约保证金率
void TdApi::queryMarginRate(const std::string & instrument){
    CThostFtdcQryInstrumentMarginRateField myreq = CThostFtdcQryInstrumentMarginRateField();
    memset(&myreq, 0, sizeof(myreq));

    user_id_.copy(myreq.InvestorID,sizeof(myreq.InvestorID));
    broker_id_.copy(myreq.BrokerID, sizeof(myreq.BrokerID));
    StrValueAssign(instrument,myreq.InstrumentID);
//请求查询合约保证金率
    int ret = this->api->ReqQryInstrumentMarginRate(&myreq, nextRequestId());
    if(ret){
        std::stringstream ss;
        ss<<"ReqQryInstrumentMarginRate Failed, Code: " << ret ;
        Application::instance()->getLogger().error(ss.str());
    }

}

// http  用户触发查询
int TdApi::queryInstrumentInfo(const std::string& instrument){
    std::lock_guard<std::mutex> lock(mutex_query_);

    if( !logined_){
        return -1;
    }
    std::this_thread::sleep_for(std::chrono::seconds(1));
    queryCommissionRate(instrument,"");
    std::this_thread::sleep_for(std::chrono::seconds(1));
    queryMarginRate(instrument);
    std::this_thread::sleep_for(std::chrono::seconds(1));
//    queryDepthMarketData(instrument,"");
    queryInstrument(instrument);
    std::this_thread::sleep_for(std::chrono::seconds(1));
    return 0;
}



void TdApi::queryAccount(){
    SCOPED_LOCK
//    dict req;
//    reqQryTradingAccount(req,nextRequestId());
    Application::instance()->getLogger().debug("queryAccount() ..");

    CThostFtdcQryTradingAccountField myreq = CThostFtdcQryTradingAccountField();
    memset(&myreq, 0, sizeof(myreq));

//    getStr(req, "CurrencyID", myreq.CurrencyID);
//    getStr(req, "InvestorID", myreq.InvestorID);
//    getChar(req, "BizType", &myreq.BizType);
//    getStr(req, "BrokerID", myreq.BrokerID);

    broker_id_.copy(myreq.BrokerID,sizeof(myreq.BrokerID));
    user_id_.copy(myreq.InvestorID, sizeof(myreq.InvestorID));
    int ret = this->api->ReqQryTradingAccount(&myreq, nextRequestId());

    this->onQueryResult("queryAccount",ret,"");


}


void TdApi::onQueryResult(const std::string& event,const int ret,const std::string & errmsg){
    if(ret){
        std::stringstream ss;
        Application::instance()->getLogger().error(ss.str());
        ss << "Code:" << ret;
        if( ret == -1){
//            ss.clear();
            ss << " Network Failed ";
        } else if( ret == -2){
            ss << " Pending Requests Exceed Limit";
        }else if( ret == -3){
            ss << " Sending Speed Exceed Limit";
        }
        ss << " " << errmsg;
        Application::instance()->getLogger().error(ss.str());
        this->onError(event,ret,ss.str());
    }
}

void TdApi::queryOrder(){
    SCOPED_LOCK
    Application::instance()->getLogger().debug("queryOrder()..");
    CThostFtdcQryOrderField myreq;
    memset(&myreq, 0, sizeof(myreq));
//    orders_.clear();
    orders_back_.clear();
    int ret = api->ReqQryOrder(&myreq, nextRequestId());
    if(ret){
        std::stringstream ss;
        ss<<"ReqQryOrder Failed, Code: " << ret ;
        Application::instance()->getLogger().error(ss.str());
    }
}

// 查询成交记录
void TdApi::queryTrade(){
    SCOPED_LOCK
    CThostFtdcQryTradeField req;
    memset(&req, 0, sizeof(req));
    trades_.clear();
    int ret = api->ReqQryTrade(&req,nextRequestId());
    if(ret){
        std::stringstream ss;
        ss<<"ReqQryTrade Failed, Code: " << ret ;
        Application::instance()->getLogger().error(ss.str());
    }
}

void TdApi::queryPosition(){
    SCOPED_LOCK
//    dict req;
//    req.set
//    req['BrokerID'] = broker_id_;
//    req['InvestorID'] = user_id_;
//    reqQryInvestorPosition(req, nextRequestId() );
    Application::instance()->getLogger().debug("queryPosition()..");

    CThostFtdcQryInvestorPositionField myreq = CThostFtdcQryInvestorPositionField();
    memset(&myreq, 0, sizeof(myreq));
//    getStr(req, "InstrumentID", myreq.InstrumentID);
//    getStr(req, "InvestorID", myreq.InvestorID);
//    getStr(req, "ExchangeID", myreq.ExchangeID);
//    getStr(req, "BrokerID", myreq.BrokerID);

    broker_id_.copy(myreq.BrokerID,sizeof(myreq.BrokerID));
    user_id_.copy(myreq.InvestorID, sizeof(myreq.InvestorID));
//    positions_.clear();
    positions_back_.clear();
    int i = this->api->ReqQryInvestorPosition(&myreq, nextRequestId());
    this->onQueryResult("queryPosition",i,"");
}

void TdApi::queryDepthMarketData(const std::string& instrument, const std::string& exchange){
    SCOPED_LOCK
    //    dict req;
//    req['InstrumentID'] = instrument;
//    req['ExchangeID'] = exchange;
//
//    reqQryInvestorPosition(req, nextRequestId() );
}

void TdApi::queryInstrument(const std::string& instrument, const std::string& exchange){
    SCOPED_LOCK

    CThostFtdcQryInstrumentField req;
    memset(&req,0,sizeof(req));
    api->ReqQryInstrument(&req,nextRequestId());
}

//查询交易手续费
void TdApi::queryCommissionRate(const std::string& instrument, const std::string& exchange){
    SCOPED_LOCK

    CThostFtdcQryInstrumentCommissionRateField myreq = CThostFtdcQryInstrumentCommissionRateField();
    memset(&myreq, 0, sizeof(myreq));

    instrument.copy(myreq.InstrumentID, sizeof myreq.InstrumentID );
    user_id_.copy(myreq.InvestorID,sizeof(myreq.InvestorID));
    broker_id_.copy(myreq.BrokerID,sizeof(myreq.BrokerID));
    exchange.copy(myreq.ExchangeID,sizeof(myreq.ExchangeID));

    int i = this->api->ReqQryInstrumentCommissionRate(&myreq, nextRequestId());
    std::stringstream ss;
    ss << "queryCommissionRate() callret:" << i ;
    Application::instance()->getLogger().debug( ss.str());
}




std::string TdApi::sendOrder(const OrderRequest& req){


    CThostFtdcInputOrderField r;
    memset(&r, 0, sizeof(r));

    StrValueAssign(req.symbol, r.InstrumentID);
    r.LimitPrice =  req.price;
    r.VolumeTotalOriginal = req.volume;
    r.Direction = req.direction;
    StrValueAssign(req.offset,r.CombOffsetFlag);
    StrValueAssign(user_id_ , r.InvestorID);
    StrValueAssign(user_id_ , r.UserID);
    StrValueAssign(broker_id_ , r.BrokerID);
    StrValueAssign( std::string("1") , r.CombHedgeFlag);
//    StrValueAssign( std::string("DCE") , r.ExchangeID);
    StrValueAssign( req.exchange_id , r.ExchangeID);

//    r.ContingentCondition = THOST_FTDC_CC_Immediately ; // 立即触发
    r.ContingentCondition = req.cc ; // 立即触发
    r.ForceCloseReason = THOST_FTDC_FCC_NotForceClose;
    r.IsAutoSuspend = 0;
//    r.TimeCondition = THOST_FTDC_TC_GFD; // 当日有效
    r.TimeCondition = req.tc; // 当日有效
    r.VolumeCondition = req.vc;  // 任何数量
    //# 判断FAK和FOK
    // FOK
    r.OrderPriceType = req.price_type; // THOST_FTDC_OPT_LimitPrice;
//    r.TimeCondition = THOST_FTDC_TC_IOC; // 立即完成，否则撤销
//    r.VolumeCondition = THOST_FTDC_VC_CV;  // 全部数量
//    r.VolumeCondition = THOST_FTDC_VC_CV;  // 全部数量

    r.RequestID = nextRequestId();
    r.MinVolume = 1;

    order_ref_ +=1 ;
    std::stringstream ss;
    ss<< order_ref_;
    StrValueAssign(ss.str(),r.OrderRef);

    std::string order_id;
    int ret = api->ReqOrderInsert(&r, r.RequestID);
    if(ret){
        std::stringstream ss;
        ss<<"SendOrder Failed, Code: " << ret ;
        Application::instance()->getLogger().error(ss.str());
    }


//     *  UserOrderId : A-FrontID-SessionID-OrderRef
//     *  SysOrderId : B-ExchangeID-OrderSysID
//     *
    ss.clear();
    ss.str("");
    ss<< "A#" << front_id_ <<"#"<< session_id_ << "#" << (int)order_ref_;
    order_id = ss.str();
    return order_id;
}


// 查询 成交记录
void TdApi::processRspQryTrade(Task task)
{
    SCOPED_LOCK
//    static std::vector< CThostFtdcTradeField > trades;

	CThostFtdcTradeField task_data = any_cast<CThostFtdcTradeField>(task.task_data);

	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//
//	this->onRspQryTrade(data, error, task.task_id, task.task_last);
    Application::instance()->getLogger().debug("<< processRspQryTrade() ..");
    trades_.push_back( task_data);

};


void TdApi::processRspAuthenticate(Task task)
{
//	PyLock lock;
	CThostFtdcRspAuthenticateField task_data = any_cast<CThostFtdcRspAuthenticateField>(task.task_data);
//	dict data;
//	data["UserID"] = task_data.UserID;
//	data["BrokerID"] = task_data.BrokerID;
//	data["UserProductInfo"] = task_data.UserProductInfo;
//
	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;
//
//	this->onRspAuthenticate(data, error, task.task_id, task.task_last);
    if(task_error.ErrorID == 0){
        authed_ = true;
        this->login();
        Application::instance()->getLogger().info("user authenticated okay.");
    }else{
        std::stringstream ss;
        ss << "authenticated error. code:" << task_error.ErrorID;
        Application::instance()->getLogger().error(ss.str());
    }
};



// 撤单
int TdApi::cancelOrder(const CancelOrderRequest& req){

//    req['InstrumentID'] = cancelOrderReq.symbol
//    req['ExchangeID'] = cancelOrderReq.exchange
//    req['OrderRef'] = cancelOrderReq.orderID
//    req['FrontID'] = cancelOrderReq.frontID
//    req['SessionID'] = cancelOrderReq.sessionID
//
//    req['ActionFlag'] = defineDict['THOST_FTDC_AF_Delete']
//    req['BrokerID'] = self.brokerID
//    req['InvestorID'] = self.userID
//
//    req['RequestID'] = cancelOrderReq.request_id
//    self.reqOrderAction(req, cancelOrderReq.request_id)

    CThostFtdcInputOrderActionField r;
    memset(&r, 0, sizeof(r));

//    StrValueAssign(req.symbol,r.InstrumentID);
    StrValueAssign(req.exchange, r.ExchangeID);
    StrValueAssign(req.order_sys_id , r.OrderSysID);
    StrValueAssign(broker_id_ , r.BrokerID );
    StrValueAssign(user_id_ , r.InvestorID);
    StrValueAssign(req.order_ref, r.OrderRef);
    r.ActionFlag = THOST_FTDC_AF_Delete;
    r.FrontID = req.front_id;
    r.SessionID = req.session_id;


    int ret = api->ReqOrderAction(&r,nextRequestId());

    if(ret){
        std::stringstream ss;
        ss<<"cancelOrder Failed, Code: " << ret ;
        Application::instance()->getLogger().error(ss.str());
    }

    return 0;
}


Json::Value TdApi::getAccountInfo(){
    SCOPED_LOCK
    Json::Value value;
    value["BrokerID"] = ftd_trade_account_.BrokerID;
    value["AccountID"] = ftd_trade_account_.AccountID;
    value["Deposit"] = ftd_trade_account_.Deposit;
    value["Withdraw"] = ftd_trade_account_.Withdraw;
    value["FrozenMargin"] = ftd_trade_account_.FrozenMargin;
    value["FrozenCash"] = ftd_trade_account_.FrozenCash;
    value["CurrMargin"] = ftd_trade_account_.CurrMargin;
    value["CloseProfit"] = ftd_trade_account_.CloseProfit;
    value["PositionProfit"] = ftd_trade_account_.PositionProfit;
    value["Balance"] = ftd_trade_account_.Balance;
    value["Available"] = ftd_trade_account_.Available;
    value["WithdrawQuota"] = ftd_trade_account_.WithdrawQuota;
    value["TradingDay"] = ftd_trade_account_.TradingDay;
    value["SettlementID"] = ftd_trade_account_.SettlementID;
    return value;
}

Json::Value TdApi::getPositions(){
    SCOPED_LOCK
    Json::Value value;
    for(auto & pos : positions_){ //CThostFtdcInvestorPositionField
//        auto & pos = itr.second;
        Json::Value node;
        node["InstrumentID"] = pos.InstrumentID;
        node["PosiDirection"] = std::string(1,pos.PosiDirection);
        node["HedgeFlag"] = std::string(1,pos.HedgeFlag);
        node["PositionDate"] = std::string(1,pos.PositionDate);
        node["YdPosition"] = pos.YdPosition;
        node["Position"] = pos.Position;
        node["LongFrozen"] = pos.LongFrozen;
        node["ShortFrozen"] = pos.ShortFrozen;
        node["LongFrozenAmount"] = pos.LongFrozenAmount;
        node["ShortFrozenAmount"] = pos.ShortFrozenAmount;
        node["OpenVolume"] = pos.OpenVolume;
        node["CloseVolume"] = pos.CloseVolume;
        node["OpenAmount"] = pos.OpenAmount;
        node["CloseAmount"] = pos.CloseAmount;
        node["PositionCost"] = pos.PositionCost;
        node["PreMargin"] = pos.PreMargin;
        node["UseMargin"] = pos.UseMargin;
        node["FrozenMargin"] = pos.FrozenMargin;
        node["FrozenCash"] = pos.FrozenCash;
        node["FrozenCommission"] = pos.FrozenCommission;
        node["CashIn"] = pos.CashIn;
        node["Commission"] = pos.Commission;
        node["CloseProfit"] = pos.CloseProfit;
        node["PositionProfit"] = pos.PositionProfit;
        node["TradingDay"] = pos.TradingDay;
        node["SettlementID"] = pos.SettlementID;
        node["OpenCost"] = pos.OpenCost;
        node["ExchangeMargin"] = pos.ExchangeMargin;
        node["TodayPosition"] = pos.TodayPosition;
        node["MarginRateByMoney"] = pos.MarginRateByMoney;
        node["MarginRateByVolume"] = pos.MarginRateByVolume;
        node["ExchangeID"] = pos.ExchangeID;
        node["YdStrikeFrozen"] = pos.YdStrikeFrozen;
        value.append(node);
    }
    return value;
}

//返回所有当前委托
// Just get current orders.
Json::Value TdApi::getOrders( std::string& user_no,  std::string& trans_no){
    SCOPED_LOCK
    Json::Value value;
    std::replace(user_no.begin(),user_no.end(),'.','#');
    std::replace(trans_no.begin(),trans_no.end(),'.','#');


    for(auto itr : orders_){
        Json::Value node;
        CThostFtdcOrderField& order = itr.second;
//        CThostFtdcOrderField& order = itr;
        node["InstrumentID"] = order.InstrumentID;
        node["OrderRef"] = order.OrderRef;
        node["UserID"] = order.UserID;
        node["OrderPriceType"] = order.OrderPriceType;
        node["Direction"] = std::string(1,order.Direction);
        node["CombOffsetFlag"] = order.CombOffsetFlag;
        node["CombHedgeFlag"] = order.CombHedgeFlag;
        node["LimitPrice"] = order.LimitPrice;
        node["VolumeTotalOriginal"] = order.VolumeTotalOriginal;
        node["TimeCondition"] = std::string(1,order.TimeCondition);
        node["GTDDate"] = order.GTDDate;
        node["VolumeCondition"] = std::string(1,order.VolumeCondition);
        node["MinVolume"] = order.MinVolume;
        node["ContingentCondition"] = order.ContingentCondition;
        node["StopPrice"] = order.StopPrice;
        node["ForceCloseReason"] = std::string(1,order.ForceCloseReason);
        node["IsAutoSuspend"] = order.IsAutoSuspend;
        node["RequestID"] = order.RequestID;
        node["OrderLocalID"] = order.OrderLocalID;
        node["ExchangeID"] = order.ExchangeID;
        node["ClientID"] = order.ClientID;
        node["OrderSubmitStatus"] = order.OrderSubmitStatus;
        node["NotifySequence"] = order.NotifySequence;
        node["TradingDay"] = order.TradingDay;
        node["SettlementID"] = order.SettlementID;
        node["OrderSysID"] = order.OrderSysID;
        node["OrderSource"] = order.OrderSource;
        node["OrderStatus"] = order.OrderStatus;
        node["OrderType"] = order.OrderType;
        node["VolumeTraded"] = order.VolumeTraded;
        node["VolumeTotal"] = order.VolumeTotal;
        node["InsertDate"] = order.InsertDate;
        node["InsertTime"] = order.InsertTime;
        node["ActiveTime"] = order.ActiveTime;
        node["SuspendTime"] = order.SuspendTime;
        node["UpdateTime"] = order.UpdateTime;
        node["CancelTime"] = order.CancelTime;
        node["SequenceNo"] = order.SequenceNo;
        node["FrontID"] = order.FrontID;
        node["SessionID"] = order.SessionID;
        node["UserProductInfo"] = order.UserProductInfo;
        node["StatusMsg"] = order.StatusMsg;
        node["UserForceClose"] = order.UserForceClose;
        node["BrokerOrderSeq"] = order.BrokerOrderSeq;
        node["BranchID"] = order.BranchID;

        if( user_no.size()){
            std::stringstream ss;
            ss<< "A#" << order.FrontID <<"#"<< order.SessionID << "#" << StrFromDataVariable(order.OrderRef);
            if( ss.str() == user_no){
                value.append(node);
            }
        }else if ( trans_no.size()){
            std::stringstream ss;
            ss<< "B#" << StrFromDataVariable(order.ExchangeID) <<"#"<< StrFromDataVariable(order.OrderSysID );
            if( ss.str() == trans_no){
                value.append(node);
            }
        }else {
            value.append(node);
        }
    }
    return value;
}

Json::Value TdApi::getTradeRecords(){
    SCOPED_LOCK


    Json::Value value;
    for(auto& trade : trades_){
        Json::Value node;
//        CThostFtdcTradeField& order = itr.second;
        node["InstrumentID"] = trade.InstrumentID;
        node["OrderRef"] = trade.OrderRef;
        node["UserID"] = trade.UserID;
        node["ExchangeID"] = trade.ExchangeID;
        node["TradeID"] = trade.TradeID;
        node["Direction"] = std::string(1,trade.Direction);
        node["OrderSysID"] = trade.OrderSysID;
        node["ParticipantID"] = trade.ParticipantID;
        node["ClientID"] = trade.ClientID;
        node["TradingRole"] = trade.TradingRole;
        node["ExchangeInstID"] = trade.ExchangeInstID;
        node["OffsetFlag"] = trade.OffsetFlag;
        node["HedgeFlag"] = std::string(1, trade.HedgeFlag);
        node["Price"] = trade.Price;
        node["Volume"] = trade.Volume;
        node["TradeDate"] = trade.TradeDate;
        node["TradeTime"] = trade.TradeTime;
        node["TradeType"] = trade.TradeType;
        node["PriceSource"] = trade.PriceSource;
        node["TraderID"] = trade.TraderID;
        node["OrderLocalID"] = trade.OrderLocalID;
        node["ClearingPartID"] = trade.ClearingPartID;
        node["BusinessUnit"] = trade.BusinessUnit;
        node["SequenceNo"] = trade.SequenceNo;
        node["TradingDay"] = trade.TradingDay;
        node["SettlementID"] = trade.SettlementID;
        node["BrokerOrderSeq"] = trade.BrokerOrderSeq;
        node["TradeSource"] = trade.TradeSource;


        value.append(node);
    }
    return value;
}

Json::Value TdApi::getInstrumentInfo(const std::string& instrument){
    SCOPED_LOCK
    Json::Value value;
    value["symbol"] = instrument;

    {
        auto itr = instruments_.find(instrument);
        if( itr != instruments_.end()){
            Json::Value node;
            auto & r = itr->second;
            node["InstrumentID"] =  r.InstrumentID;
            node["ExchangeID"] =  r.ExchangeID;
            node["InstrumentName"] =  r.InstrumentName;
            node["ExchangeInstID"] =  r.ExchangeInstID;
            node["ProductID"] =  r.ProductID;
            node["ProductClass"] =  r.ProductClass;
            node["DeliveryYear"] =  r.DeliveryYear;
            node["DeliveryMonth"] =  r.DeliveryMonth;
            node["MaxMarketOrderVolume"] =  r.MaxMarketOrderVolume;
            node["MinMarketOrderVolume"] =  r.MinMarketOrderVolume;
            node["MaxLimitOrderVolume"] =  r.MaxLimitOrderVolume;
            node["MinLimitOrderVolume"] =  r.MinLimitOrderVolume;
            node["VolumeMultiple"] =  r.VolumeMultiple;
            node["PriceTick"] =  r.PriceTick;
            node["CreateDate"] =  r.CreateDate;
            node["OpenDate"] =  r.OpenDate;
            node["ExpireDate"] =  r.ExpireDate;
            node["StartDelivDate"] =  r.StartDelivDate;
            node["EndDelivDate"] =  r.EndDelivDate;
            node["InstLifePhase"] =  r.InstLifePhase;
            node["IsTrading"] =  r.IsTrading;
            node["PositionType"] =  r.PositionType;
            node["PositionDateType"] =  r.PositionDateType;
            node["LongMarginRatio"] =  r.LongMarginRatio;
            node["ShortMarginRatio"] =  r.ShortMarginRatio;
            node["MaxMarginSideAlgorithm"] =  r.MaxMarginSideAlgorithm;
            node["UnderlyingInstrID"] =  r.UnderlyingInstrID;
            node["StrikePrice"] =  r.StrikePrice;
            node["OptionsType"] =  r.OptionsType;
            node["UnderlyingMultiple"] =  r.UnderlyingMultiple;
            node["CombinationType"] =  r.CombinationType;
#ifndef _CHUANTOU
            node["MinBuyVolume"] =  r.MinBuyVolume;
            node["MinSellVolume"] =  r.MinSellVolume;
            node["InstrumentCode"] =  r.InstrumentCode;
#endif
            value["instrument"] = node;
        }
    }
    // margin rate
    {
        auto itr = margin_rates_.find(instrument);
        if (itr != margin_rates_.end()) {
            Json::Value node;
            auto &r = itr->second;
            node["InstrumentID"] = r.InstrumentID;
            node["InvestorRange"] = r.InvestorRange;
            node["BrokerID"] = r.BrokerID;
            node["InvestorID"] = r.InvestorID;
            node["HedgeFlag"] = std::string(1,r.HedgeFlag);
            node["LongMarginRatioByMoney"] = r.LongMarginRatioByMoney;
            node["LongMarginRatioByVolume"] = r.LongMarginRatioByVolume;
            node["ShortMarginRatioByMoney"] = r.ShortMarginRatioByMoney;
            node["ShortMarginRatioByVolume"] = r.ShortMarginRatioByVolume;
            node["IsRelative"] = r.IsRelative;

            value["margin_rate"] = node;
        }

    }

    // commission rate
    {
        auto itr = commission_rates_.find(instrument);
        for(auto itr: commission_rates_){
            auto & name = itr.first;
            if( instrument.find_first_of(name) == std::string::npos){
                continue;
            }

//        if (itr != commission_rates_.end()) {
            Json::Value node;
            auto &r = itr.second;
            node["InstrumentID"] = r.InstrumentID;
            node["InvestorRange"] = r.InvestorRange;
            node["BrokerID"] = r.BrokerID;
            node["InvestorID"] = r.InvestorID;
            node["OpenRatioByMoney"] = r.OpenRatioByMoney;
            node["OpenRatioByVolume"] = r.OpenRatioByVolume;
            node["CloseRatioByMoney"] = r.CloseRatioByMoney;
            node["CloseRatioByVolume"] = r.CloseRatioByVolume;
            node["CloseTodayRatioByMoney"] = r.CloseTodayRatioByMoney;
            node["CloseTodayRatioByVolume"] = r.CloseTodayRatioByVolume;
            node["ExchangeID"] = r.ExchangeID;
            node["BizType"] = r.BizType;

            value["commission_rate"] = node;
        }

    }

    return value;
}

void TdApi::disconnect(){

}

TdApi& TdApi::instance(){
    static TdApi api;
    return api;
}

static std::thread * joinThread = NULL;


void sig_usr(int){
    std::cout<< "SIGUSR1 .." << std::endl;
}


int main_loop() {

    if (signal(SIGUSR1, sig_usr) == SIG_ERR){
        printf("can not catch SIGUSR1\n");
    }
    Config & cfg = Application::instance()->getConfig();

    connection_options.host = cfg.get_string("redis.host","127.0.0.1");
    connection_options.port = cfg.get_int("redis.port",6379); 			// The default port is 6379.
//	connection_options.password = "auth";   // Optional. No password by default.
    connection_options.db = cfg.get_int("redis.db",0);
    connection_options.socket_timeout = std::chrono::milliseconds(200);

    pubchan_event_name_ = Application::instance()->getConfig().get_string("ctp.pubchan_event_name","zsqh-prd");
// Connect to Redis server with a single connection.
    redis_ = new Redis(connection_options);

    HttpService::instance()->init(cfg);
    HttpService::instance()->open();

    TdApi::instance().start();


//    TdApi::instance().join();
    joinThread = new std::thread([]{
        Application::instance()->getLogger().debug("CTP Api Thread Join..");
        TdApi::instance().join();
    });

    return 0;
}



void TdApi::onError(const std::string& event,const int errcode,const std::string & errmsg){
    Json::Value node;
    node["event"] = "event_error";
    node["errcode"] = errcode;
    node["errmsg"] = errmsg;
    node["conn_url"] = pubchan_event_name_;
    std::string json_text = node.toStyledString();
    redis_->publish(pubchan_event_name_, json_text);
}

/*
 * vim ~/.gdbinit
 *
 * handle SIGUSR1 noprint nostop
 *
 *
 */