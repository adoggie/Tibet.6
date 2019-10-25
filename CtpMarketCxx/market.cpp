// vnctpmd.cpp : 定义 DLL 应用程序的导出函数。
//

#include "market.h"
#include "app.h"
#include <jsoncpp/json/json.h>
#include <boost/algorithm/string.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>


///-------------------------------------------------------------------------------------
///从Python对象到C++类型转换用的函数
///-------------------------------------------------------------------------------------
/*
void getInt(dict d, string key, int *value)
{
	if (d.has_key(key))		//检查字典中是否存在该键值
	{
		object o = d[key];	//获取该键值
		extract<int> x(o);	//创建提取器
		if (x.check())		//如果可以提取
		{
			*value = x();	//对目标整数指针赋值
		}
	}
};

void getDouble(dict d, string key, double *value)
{
	if (d.has_key(key))
	{
		object o = d[key];
		extract<double> x(o);
		if (x.check())
		{
			*value = x();
		}
	}
};

void getStr(dict d, string key, char *value)
{
	if (d.has_key(key))
	{
		object o = d[key];
		extract<string> x(o);
		if (x.check())
		{
			string s = x();
			const char *buffer = s.c_str();
			//对字符串指针赋值必须使用strcpy_s, vs2013使用strcpy编译通不过
			//+1应该是因为C++字符串的结尾符号？不是特别确定，不加这个1会出错
#ifdef _MSC_VER //WIN32
			strcpy_s(value, strlen(buffer) + 1, buffer);
#elif __GNUC__
			strncpy(value, buffer, strlen(buffer) + 1);
#endif
		}
	}
};

void getChar(dict d, string key, char *value)
{
	if (d.has_key(key))
	{
		object o = d[key];
		extract<string> x(o);
		if (x.check())
		{
			string s = x();
			const char *buffer = s.c_str();
			*value = *buffer;
		}
	}
};

 */

void assign(char* dest,size_t dest_size,const char* src){
	size_t size = strlen(src);
	dest_size = dest_size - 1;
	if( size > dest_size  ){
		size = dest_size;
	}
	memcpy(dest,src,size);
}

#define ASSIGN(dest,src) assign(dest,sizeof(dest),src)

///-------------------------------------------------------------------------------------
///C++的回调函数将数据保存到队列中
///-------------------------------------------------------------------------------------

void MdApi::OnFrontConnected()
{
	Task task = Task();
	task.task_name = ONFRONTCONNECTED;
	this->task_queue.push(task);
};

void MdApi::OnFrontDisconnected(int nReason)
{
	Task task = Task();
	task.task_name = ONFRONTDISCONNECTED;
	task.task_id = nReason;
	this->task_queue.push(task);
};

void MdApi::OnHeartBeatWarning(int nTimeLapse)
{
	Task task = Task();
	task.task_name = ONHEARTBEATWARNING;
	task.task_id = nTimeLapse;
	this->task_queue.push(task);
};

void MdApi::OnRspUserLogin(CThostFtdcRspUserLoginField *pRspUserLogin, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUSERLOGIN;

	if (pRspUserLogin)
	{
		task.task_data = *pRspUserLogin;
	}
	else
	{
		CThostFtdcRspUserLoginField empty_data = CThostFtdcRspUserLoginField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}

	if (pRspInfo)
	{
		task.task_error = *pRspInfo;
	}
	else
	{
		CThostFtdcRspInfoField empty_error = CThostFtdcRspInfoField();
		memset(&empty_error, 0, sizeof(empty_error));
		task.task_error = empty_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspUserLogout(CThostFtdcUserLogoutField *pUserLogout, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUSERLOGOUT;

	if (pUserLogout)
	{
		task.task_data = *pUserLogout;
	}
	else
	{
		CThostFtdcUserLogoutField empty_data = CThostFtdcUserLogoutField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}

	if (pRspInfo)
	{
		task.task_error = *pRspInfo;
	}
	else
	{
		CThostFtdcRspInfoField empty_error = CThostFtdcRspInfoField();
		memset(&empty_error, 0, sizeof(empty_error));
		task.task_error = empty_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspError(CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPERROR;

	if (pRspInfo)
	{
		task.task_error = *pRspInfo;
	}
	else
	{
		CThostFtdcRspInfoField empty_error = CThostFtdcRspInfoField();
		memset(&empty_error, 0, sizeof(empty_error));
		task.task_error = empty_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPSUBMARKETDATA;

	if (pSpecificInstrument)
	{
		task.task_data = *pSpecificInstrument;
	}
	else
	{
		CThostFtdcSpecificInstrumentField empty_data = CThostFtdcSpecificInstrumentField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}

	if (pRspInfo)
	{
		task.task_error = *pRspInfo;
	}
	else
	{
		CThostFtdcRspInfoField empty_error = CThostFtdcRspInfoField();
		memset(&empty_error, 0, sizeof(empty_error));
		task.task_error = empty_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUNSUBMARKETDATA;

	if (pSpecificInstrument)
	{
		task.task_data = *pSpecificInstrument;
	}
	else
	{
		CThostFtdcSpecificInstrumentField empty_data = CThostFtdcSpecificInstrumentField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}

	if (pRspInfo)
	{
		task.task_error = *pRspInfo;
	}
	else
	{
		CThostFtdcRspInfoField empty_error = CThostFtdcRspInfoField();
		memset(&empty_error, 0, sizeof(empty_error));
		task.task_error = empty_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspSubForQuoteRsp(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPSUBFORQUOTERSP;

	if (pSpecificInstrument)
	{
		task.task_data = *pSpecificInstrument;
	}
	else
	{
		CThostFtdcSpecificInstrumentField empty_data = CThostFtdcSpecificInstrumentField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}

	if (pRspInfo)
	{
		task.task_error = *pRspInfo;
	}
	else
	{
		CThostFtdcRspInfoField empty_error = CThostFtdcRspInfoField();
		memset(&empty_error, 0, sizeof(empty_error));
		task.task_error = empty_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRspUnSubForQuoteRsp(CThostFtdcSpecificInstrumentField *pSpecificInstrument, CThostFtdcRspInfoField *pRspInfo, int nRequestID, bool bIsLast)
{
	Task task = Task();
	task.task_name = ONRSPUNSUBFORQUOTERSP;

	if (pSpecificInstrument)
	{
		task.task_data = *pSpecificInstrument;
	}
	else
	{
		CThostFtdcSpecificInstrumentField empty_data = CThostFtdcSpecificInstrumentField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}

	if (pRspInfo)
	{
		task.task_error = *pRspInfo;
	}
	else
	{
		CThostFtdcRspInfoField empty_error = CThostFtdcRspInfoField();
		memset(&empty_error, 0, sizeof(empty_error));
		task.task_error = empty_error;
	}
	task.task_id = nRequestID;
	task.task_last = bIsLast;
	this->task_queue.push(task);
};

void MdApi::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField *pDepthMarketData)
{
	Task task = Task();
	task.task_name = ONRTNDEPTHMARKETDATA;

	if (pDepthMarketData)
	{
		task.task_data = *pDepthMarketData;
	}
	else
	{
		CThostFtdcDepthMarketDataField empty_data = CThostFtdcDepthMarketDataField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}
	this->task_queue.push(task);
};

void MdApi::OnRtnForQuoteRsp(CThostFtdcForQuoteRspField *pForQuoteRsp)
{
	Task task = Task();
	task.task_name = ONRTNFORQUOTERSP;

	if (pForQuoteRsp)
	{
		task.task_data = *pForQuoteRsp;
	}
	else
	{
		CThostFtdcForQuoteRspField empty_data = CThostFtdcForQuoteRspField();
		memset(&empty_data, 0, sizeof(empty_data));
		task.task_data = empty_data;
	}
	this->task_queue.push(task);
};



///-------------------------------------------------------------------------------------
///工作线程从队列中取出数据，转化为python对象后，进行推送
///-------------------------------------------------------------------------------------

void MdApi::processTask()
{
	while (1)
	{
		Task task = this->task_queue.wait_and_pop();

		switch (task.task_name)
		{
		case ONFRONTCONNECTED:
		{
			this->processFrontConnected(task);
			break;
		}

		case ONFRONTDISCONNECTED:
		{
			this->processFrontDisconnected(task);
			break;
		}

		case ONHEARTBEATWARNING:
		{
			this->processHeartBeatWarning(task);
			break;
		}

		case ONRSPUSERLOGIN:
		{
			this->processRspUserLogin(task);
			break;
		}

		case ONRSPUSERLOGOUT:
		{
			this->processRspUserLogout(task);
			break;
		}

		case ONRSPERROR:
		{
			this->processRspError(task);
			break;
		}

		case ONRSPSUBMARKETDATA:
		{
			this->processRspSubMarketData(task);
			break;
		}

		case ONRSPUNSUBMARKETDATA:
		{
			this->processRspUnSubMarketData(task);
			break;
		}

		case ONRSPSUBFORQUOTERSP:
		{
			this->processRspSubForQuoteRsp(task);
			break;
		}

		case ONRSPUNSUBFORQUOTERSP:
		{
			this->processRspUnSubForQuoteRsp(task);
			break;
		}

		case ONRTNDEPTHMARKETDATA:
		{
			this->processRtnDepthMarketData(task);
			break;
		}

		case ONRTNFORQUOTERSP:
		{
			this->processRtnForQuoteRsp(task);
			break;
		}
		};
	}
};

void MdApi::processFrontConnected(Task task)
{
//	PyLock lock;
	this->onFrontConnected();
};

void MdApi::processFrontDisconnected(Task task)
{
//	PyLock lock;
	this->onFrontDisconnected(task.task_id);
};

void MdApi::processHeartBeatWarning(Task task)
{
//	PyLock lock;
	this->onHeartBeatWarning(task.task_id);
};

void MdApi::processRspUserLogin(Task task)
{
//	PyLock lock;
	CThostFtdcRspUserLoginField task_data = any_cast<CThostFtdcRspUserLoginField>(task.task_data);
//	dict data;
//	data["CZCETime"] = task_data.CZCETime;
//	data["SHFETime"] = task_data.SHFETime;
//	data["MaxOrderRef"] = task_data.MaxOrderRef;
//	data["INETime"] = task_data.INETime;
//	data["UserID"] = task_data.UserID;
//	data["TradingDay"] = task_data.TradingDay;
//	data["SessionID"] = task_data.SessionID;
//	data["SystemName"] = task_data.SystemName;
//	data["FrontID"] = task_data.FrontID;
//	data["FFEXTime"] = task_data.FFEXTime;
//	data["BrokerID"] = task_data.BrokerID;
//	data["DCETime"] = task_data.DCETime;
//	data["LoginTime"] = task_data.LoginTime;

	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;

	this->onRspUserLogin(&task_data, &task_error, task.task_id, task.task_last);
};

void MdApi::processRspUserLogout(Task task)
{
//	PyLock lock;
	CThostFtdcUserLogoutField task_data = any_cast<CThostFtdcUserLogoutField>(task.task_data);
//	dict data;
//	data["UserID"] = task_data.UserID;
//	data["BrokerID"] = task_data.BrokerID;

	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;

	this->onRspUserLogout(&task_data, &task_error, task.task_id, task.task_last);
};

void MdApi::processRspError(Task task)
{
//	PyLock lock;
	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;
    if( task_error.ErrorID) {
        std::string text = (boost::format("onRspError = error-id:%d , error-msg:%s") % task_error.ErrorID %
                            task_error.ErrorMsg).str();
        Application::instance()->getLogger().error(text);
    }

//	this->onRspError(&task_error, task.task_id, task.task_last);
};

void MdApi::processRspSubMarketData(Task task)
{
//	PyLock lock;
	CThostFtdcSpecificInstrumentField task_data = any_cast<CThostFtdcSpecificInstrumentField>(task.task_data);
//	dict data;
//	data["InstrumentID"] = task_data.InstrumentID;

	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;

	this->onRspSubMarketData(&task_data, &task_error, task.task_id, task.task_last);
};

void MdApi::processRspUnSubMarketData(Task task)
{
//	PyLock lock;
	CThostFtdcSpecificInstrumentField task_data = any_cast<CThostFtdcSpecificInstrumentField>(task.task_data);
//	dict data;
//	data["InstrumentID"] = task_data.InstrumentID;

	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;

	this->onRspUnSubMarketData(&task_data, &task_error, task.task_id, task.task_last);
};

void MdApi::processRspSubForQuoteRsp(Task task)
{
//	PyLock lock;
	CThostFtdcSpecificInstrumentField task_data = any_cast<CThostFtdcSpecificInstrumentField>(task.task_data);
//	dict data;
//	data["InstrumentID"] = task_data.InstrumentID;

	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;

	this->onRspSubForQuoteRsp(&task_data, &task_error, task.task_id, task.task_last);
};

void MdApi::processRspUnSubForQuoteRsp(Task task)
{
//	PyLock lock;
	CThostFtdcSpecificInstrumentField task_data = any_cast<CThostFtdcSpecificInstrumentField>(task.task_data);
//	dict data;
//	data["InstrumentID"] = task_data.InstrumentID;

	CThostFtdcRspInfoField task_error = any_cast<CThostFtdcRspInfoField>(task.task_error);
//	dict error;
//	error["ErrorMsg"] = task_error.ErrorMsg;
//	error["ErrorID"] = task_error.ErrorID;

	this->onRspUnSubForQuoteRsp(&task_data, &task_error, task.task_id, task.task_last);
};

void MdApi::processRtnDepthMarketData(Task task)
{
//	PyLock lock;
	CThostFtdcDepthMarketDataField task_data = any_cast<CThostFtdcDepthMarketDataField>(task.task_data);
	Json::Value data;
//	dict data;
	data["HighestPrice"] = task_data.HighestPrice;
	data["BidPrice5"] = task_data.BidPrice5;
	data["BidPrice4"] = task_data.BidPrice4;
	data["BidPrice1"] = task_data.BidPrice1;
	data["BidPrice3"] = task_data.BidPrice3;
	data["BidPrice2"] = task_data.BidPrice2;
	data["LowerLimitPrice"] = task_data.LowerLimitPrice;
	data["OpenPrice"] = task_data.OpenPrice;
	data["AskPrice5"] = task_data.AskPrice5;
	data["AskPrice4"] = task_data.AskPrice4;
	data["AskPrice3"] = task_data.AskPrice3;
    data["AskPrice1"] = task_data.AskPrice1;
    data["AskPrice2"] = task_data.AskPrice2;

	data["PreClosePrice"] = task_data.PreClosePrice;

	data["PreSettlementPrice"] = task_data.PreSettlementPrice;
	data["AskVolume1"] = task_data.AskVolume1;
	data["UpdateTime"] = task_data.UpdateTime;
	data["UpdateMillisec"] = task_data.UpdateMillisec;
	data["AveragePrice"] = task_data.AveragePrice;
	data["BidVolume5"] = task_data.BidVolume5;
	data["BidVolume4"] = task_data.BidVolume4;
	data["BidVolume3"] = task_data.BidVolume3;
	data["BidVolume2"] = task_data.BidVolume2;
	data["PreOpenInterest"] = task_data.PreOpenInterest;

	data["Volume"] = task_data.Volume;
	data["AskVolume3"] = task_data.AskVolume3;
	data["AskVolume2"] = task_data.AskVolume2;
	data["AskVolume5"] = task_data.AskVolume5;
	data["AskVolume4"] = task_data.AskVolume4;
	data["UpperLimitPrice"] = task_data.UpperLimitPrice;
	data["BidVolume1"] = task_data.BidVolume1;
	data["InstrumentID"] = task_data.InstrumentID;
	data["ClosePrice"] = task_data.ClosePrice;
	data["ExchangeID"] = task_data.ExchangeID;
	data["TradingDay"] = task_data.TradingDay;
	data["PreDelta"] = task_data.PreDelta;
	data["OpenInterest"] = task_data.OpenInterest;
	data["CurrDelta"] = task_data.CurrDelta;
	data["Turnover"] = task_data.Turnover;
	data["LastPrice"] = task_data.LastPrice;
	data["SettlementPrice"] = task_data.SettlementPrice;
	data["ExchangeInstID"] = task_data.ExchangeInstID;
	data["LowestPrice"] = task_data.LowestPrice;
	data["ActionDay"] = task_data.ActionDay;
	std::string datetime = task_data.TradingDay + std::string(" ") + task_data.UpdateTime + \
			std::string(".") + boost::lexical_cast<std::string>(task_data.UpdateMillisec);
	data["DateTime"] = datetime;
    datetime = datetime.substr(0,4) +"-"+ datetime.substr(4,2) + "-" + datetime.substr(6,2) + datetime.substr(8);

	boost::posix_time::ptime pt(boost::posix_time::time_from_string(datetime));
//	boost::posix_time::ptime pt;

//    std::stringstream ss(datetime);
//    std::string format = "%Y%m%d %H:%M:%S.%f";
//    ss.imbue(std::locale(ss.getloc(), new boost::posix_time::time_input_facet(format)));//out
//    ss >> pt;
    std::stringstream ss;
    std::cout << task_data.InstrumentID << "," << data["DateTime"] << std::endl;
    ss << task_data.InstrumentID << "," << data["DateTime"] ;
    Application::instance()->getLogger().debug(ss.str());

	std::time_t ts = boost::posix_time::to_time_t(pt);
	data["Timestamp"] = Json::Value::UInt64 (ts);
	//(unsigned long)ts;

	std::string json_text = data.toStyledString();
	// ctp.pub_m1905
	std::string pubname = Application::instance()->getConfig().get_string("ctp.pub_depthmarket");
	std::string lastname = Application::instance()->getConfig().get_string("ctp.last_depthmarket");
	std::string listname = Application::instance()->getConfig().get_string("ctp.list_depthmarket");

	if( pubname.size()) {
	    pubname += task_data.InstrumentID;
		redis_->publish(pubname, json_text);
	}

	if( lastname.size() ) {
        lastname += task_data.InstrumentID;
		Json::Value::Members names = data.getMemberNames();
		std::map<std::string, std::string> entries;
		for (const auto &name : names) {
			entries[name] = data.get(name, "").asString();
		}
		redis_->hmset(lastname, entries.begin(), entries.end());
	}

	if( listname.size() ){
//        listname += task_data.InstrumentID;
		redis_->rpush(listname,json_text);
	}

	if(Application::instance()->getConfig().get_int("log.debug")){
	    Application::instance()->getLogger().debug("OnDepthMarketData :");
	    Application::instance()->getLogger().debug(json_text);
	}

};

//"%Y-%m-%d %H:%M:%S.%f"
bool ptime_from_string(boost::posix_time::ptime& pt, std::string datetime, std::string format) {
    std::stringstream ss(datetime);
    //std::locale responsible for releasing memory.
    ss.imbue(std::locale(ss.getloc(), new boost::posix_time::time_input_facet(format)));//out
    if (ss >> pt) {
        return true;
    }
    return false;
}


void MdApi::processRtnForQuoteRsp(Task task)
{
//	PyLock lock;
	CThostFtdcForQuoteRspField task_data = any_cast<CThostFtdcForQuoteRspField>(task.task_data);
//	dict data;
//	data["InstrumentID"] = task_data.InstrumentID;
//	data["ActionDay"] = task_data.ActionDay;
//	data["ExchangeID"] = task_data.ExchangeID;
//	data["TradingDay"] = task_data.TradingDay;
//	data["ForQuoteSysID"] = task_data.ForQuoteSysID;
//	data["ForQuoteTime"] = task_data.ForQuoteTime;

	this->onRtnForQuoteRsp(&task_data);
};



///-------------------------------------------------------------------------------------
///主动函数
///-------------------------------------------------------------------------------------

void MdApi::createFtdcMdApi(string pszFlowPath)
{
	this->api = CThostFtdcMdApi::CreateFtdcMdApi(pszFlowPath.c_str());
	this->api->RegisterSpi(this);
};

void MdApi::release()
{
	this->api->Release();
};

void MdApi::init()
{
	this->api->Init();
};

int MdApi::join()
{
	int i = this->api->Join();
	return i;
};

int MdApi::exit()
{
	//该函数在原生API里没有，用于安全退出API用，原生的join似乎不太稳定
	this->api->RegisterSpi(NULL);
	this->api->Release();
	this->api = NULL;
	return 1;
};

string MdApi::getTradingDay()
{
	string day = this->api->GetTradingDay();
	return day;
};

void MdApi::registerFront(string pszFrontAddress)
{
	this->api->RegisterFront((char*)pszFrontAddress.c_str());
};

int MdApi::subscribeMarketData(string instrumentID)
{
	char* buffer = (char*) instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->SubscribeMarketData(myreq, 1);
	return i;
};

int MdApi::unSubscribeMarketData(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };;
	int i = this->api->UnSubscribeMarketData(myreq, 1);
	return i;
};

int MdApi::subscribeForQuoteRsp(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };
	int i = this->api->SubscribeForQuoteRsp(myreq, 1);
	return i;
};

int MdApi::unSubscribeForQuoteRsp(string instrumentID)
{
	char* buffer = (char*)instrumentID.c_str();
	char* myreq[1] = { buffer };;
	int i = this->api->UnSubscribeForQuoteRsp(myreq, 1);
	return i;
};

int MdApi::reqUserLogin( CThostFtdcReqUserLoginField* req, int nRequestID)
{
	int i = this->api->ReqUserLogin(req, nRequestID);
	return i;
};

int MdApi::reqUserLogout(CThostFtdcUserLogoutField* req, int nRequestID)
{
//	CThostFtdcUserLogoutField myreq = CThostFtdcUserLogoutField();
//	memset(&myreq, 0, sizeof(myreq));
//	getStr(req, "UserID", myreq.UserID);
//	getStr(req, "BrokerID", myreq.BrokerID);
	int i = this->api->ReqUserLogout(req, nRequestID);
	return i;
};




bool MdApi::start(){
	ConnectionOptions connection_options;
	Config & cfg = Application::instance()->getConfig();

	connection_options.host = cfg.get_string("redis.host","127.0.0.1");
	connection_options.port = cfg.get_int("redis.port",6379); 			// The default port is 6379.
//	connection_options.password = "auth";   // Optional. No password by default.
	connection_options.db = cfg.get_int("redis.db",0);
	connection_options.socket_timeout = std::chrono::milliseconds(200);

// Connect to Redis server with a single connection.
	redis_ = new Redis(connection_options);


//	Redis redis1(connection_options);
//	ConnectionPoolOptions pool_options;
//	pool_options.size = 3;  // Pool size, i.e. max number of connections.
// Connect to Redis server with a connection pool.
//	Redis redis2(connection_options, pool_options);

//    std::vector< std::string > instruments;
    std::string text = cfg.get_string("ctp.sub_instruments");
    boost::split(instruments_,text,boost::is_any_of(", "));

    connect();
	return true;
}


void MdApi::stop(){
	this->exit();
	delete redis_;
}



bool MdApi::connect(){
	Config& cfg = Application::instance()->getConfig();
	std::string conpath = cfg.get_string("ctp.con_path","cons");
	std::string address = cfg.get_string("ctp.md_addr");
	createFtdcMdApi(conpath);
	registerFront(address);
	init();
	return true;
}

void MdApi::disconnect(){

}


void MdApi::onFrontConnected(){
	CThostFtdcReqUserLoginField req;
	memset(&req,0,sizeof(req));
	std::string userid ,password, brokerid;
	Config & cfg = Application::instance()->getConfig();
	userid = cfg.get_string("ctp.user_id");
	password = cfg.get_string("ctp.password");
	brokerid = cfg.get_string("ctp.broker_id");

	assign(req.BrokerID, sizeof(req.BrokerID),brokerid.c_str());
	reqUserLogin(&req,0);//
}

void MdApi::onFrontDisconnected(int i){
	Application::instance()->getLogger().info("front disconnected..");
}

void MdApi::onHeartBeatWarning(int i){
	Application::instance()->getLogger().debug("front heartbeat..");

}

void MdApi::onRspUserLogin(CThostFtdcRspUserLoginField* data, CThostFtdcRspInfoField* error, int id, bool last){
    Application::instance()->getLogger().info("onRspUserLogin : To subscribe Market Data");
    boost::mutex::scoped_lock lock(mtx_instruments_);
	for(auto _ : instruments_){
	    Application::instance()->getLogger().debug("subscribe: " + _);
		subscribeMarketData(_);
	}
}

void MdApi::onRspUserLogout(CThostFtdcUserLogoutField* data,
		CThostFtdcRspInfoField* error, int id, bool last) {
    Application::instance()->getLogger().info("onRspUserLogout : ");
}

//void MdApi::onRspError(CThostFtdcRspInfoField* error, int id, bool last) {
//	std::string text = (boost::format("onRspError = error-id:%d , error-msg:%s")%error->ErrorID%error->ErrorMsg).str();
//	Application::instance()->getLogger().error(text);
//}

void MdApi::onRspSubMarketData(CThostFtdcSpecificInstrumentField* data, CThostFtdcRspInfoField* error, int id, bool last) {
	std::string text = (boost::format(" onRspSubMarketData =  code:%s  error-id:%d , error-msg:%s")%data->InstrumentID%error->ErrorID%error->ErrorMsg).str();
	Application::instance()->getLogger().error(text);
};

void MdApi::onRspUnSubMarketData(CThostFtdcSpecificInstrumentField* data, CThostFtdcRspInfoField* error, int id, bool last) {

};

void MdApi::onRspSubForQuoteRsp(CThostFtdcSpecificInstrumentField* data, CThostFtdcRspInfoField* error, int id, bool last) {

};

void MdApi::onRspUnSubForQuoteRsp(CThostFtdcSpecificInstrumentField* data, CThostFtdcRspInfoField* error, int id, bool last) {

};

//void MdApi::onRtnDepthMarketData(CThostFtdcDepthMarketDataField* data) {
//	// quotes got , push it into redis pub/sub
//
//};

void MdApi::onRtnForQuoteRsp(CThostFtdcForQuoteRspField* data) {

};


MdApi service;

int main_loop(){

	service.start();
	service.join();
	return 0;
}