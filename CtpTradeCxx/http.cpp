
#include "http.h"

#include "mongoose.h"
#include <thread>
#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>
#include <jsoncpp/json/json.h>

#include "trade.h"
#include "app.h"
#include "error.h"
//#include "md5.hpp"
//#include "base64.h"


// mongoose help
// https://cesanta.com/docs/overview/intro.html
// https://github.com/cesanta/mongoose/blob/master/examples/simple_crawler/simple_crawler.c
// https://github.com/Gregwar/mongoose-cpp


/*
 * A - 室内屏  B - 室内主机  C - 新增室内设备(手机)  D - 物业服务器 E - 室外机 F - 物业App
 *
设备注册:
 	A请求B生成新设备注册地址 ( http://ip:port/../token ) , token生成需添加时间阈值，自签名之后返回给A，A生成QR码
	C 扫描 QR码，获得注册url，继而发起对B的指定ur的注册请求(携带 sn,type,os等设备相关信息),B返回C的认证码T.
	(后续所有C访问B的请求均需携带T作为有效身份识别)

注册设备查询和删除：
 A ，D 查询已注册到B的C类型设备记录 ，并可以删除指定的注册记录



 */
static const char *s_http_port = "8000";
static struct mg_serve_http_opts s_http_server_opts;
struct mg_mgr mgr;
//struct mg_connection *nc;
struct mg_bind_opts bind_opts;

//static void handle_sum_call(struct mg_connection *nc, struct http_message *hm) {
//	char n1[100], n2[100];
//	double result;
//
//	/* Get form variables */
//	mg_get_http_var(&hm->body, "n1", n1, sizeof(n1));
//	mg_get_http_var(&hm->body, "n2", n2, sizeof(n2));
//
//	/* Send headers */
//	mg_printf(nc, "%s", "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
//
//	/* Compute the result and send it back as a JSON object */
//	result = strtod(n1, NULL) + strtod(n2, NULL);
//	mg_printf_http_chunk(nc, "{ \"result\": %lf }", result);
//	mg_send_http_chunk(nc, "", 0); /* Send empty chunk, the end of response */
//}

std::string http_get_var(struct http_message *hm,const std::string& name,const std::string& def=""){
	char buf[1200];
	int ret;

	std::string val;
	ret = mg_get_http_var(&hm->body, name.c_str(), buf, sizeof(buf));
	if(ret > 0 ){
		val = buf;
	}else{
	    val = def;
	}
	return val;
}

std::string http_get_query_var(struct http_message *hm,const std::string& name,const std::string& def=""){
    char buf[1200];
    int ret;

    std::string val;
    ret = mg_get_http_var(&hm->query_string, name.c_str(), buf, sizeof(buf));
    if(ret > 0 ){
        val = buf;
    }else{
        val = def;
    }
    return val;
}

HttpHeaders_t defaultResponseHeaders(){
	return {
			{"Content-Type","application/json"},
			{"Transfer-Encoding","chunked"}
	};
}

Json::Value defaultResponseJsonData(int status=HTTP_JSON_RESULT_STATUS_OK,int errcode = Error_NoError,const char* errmsg=""){
	Json::Value data;
	data["status"] = status;
	data["errcode"] = errcode;
	data["errmsg"] = errmsg;
	if(errmsg == std::string("")){
		data["errmsg"] =  ErrorDefs.at(errcode);
	}
	return data;
}


Json::Value errorResponseJsonData(int errcode = Error_NoError,const char* errmsg=""){
	Json::Value data;
	data["status"] = HTTP_JSON_RESULT_STATUS_ERROR;
	data["errcode"] = errcode;
	data["errmsg"] = errmsg;
	if(errmsg == std::string("")){
		data["errmsg"] =  ErrorDefs.at(errcode);
	}
	return data;
}


void send_http_response(struct mg_connection *nc,const std::string& text,const HttpHeaders_t& headers){
//	mg_printf(nc, "%s", "HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n");
	mg_printf(nc, "%s", "HTTP/1.1 200 OK\r\n");
	
	
	for(auto p:headers) {
		mg_printf(nc, "%s: %s\r\n", p.first.c_str(),p.second.c_str());
	}
	mg_printf(nc, "%s", "\r\n");
	
	mg_send_http_chunk(nc, text.c_str(), text.size());
	mg_send_http_chunk(nc, "", 0);
}


void send_http_response_error(struct mg_connection *nc,int errcode = Error_NoError,const char* errmsg="") {
    Json::Value data = errorResponseJsonData(errcode,errmsg);
    std::string text = data.toStyledString();
    send_http_response(nc, text, defaultResponseHeaders());
}

void send_http_response_okay(struct mg_connection *nc,int errcode = Error_NoError,const char* errmsg="") {
    Json::Value data = defaultResponseJsonData();
    std::string text = data.toStyledString();
    send_http_response(nc, text, defaultResponseHeaders());
}

void send_http_response_result(Json::Value result,struct mg_connection *nc,int errcode = Error_NoError,const char* errmsg="") {
    Json::Value data = defaultResponseJsonData();
    data["result"] = result;
    std::string text = data.toStyledString();
    send_http_response(nc, text, defaultResponseHeaders());
}

void HttpService::ev_handler(struct mg_connection *nc, int ev, void *ev_data) {
	struct http_message *hm = (struct http_message *) ev_data;
	HttpService* http = HttpService::instance().get();
    std::string method ;
    std::string url;
    std::stringstream ss;
    std::time_t end, start;
    try {
        switch (ev) {
            case MG_EV_HTTP_REQUEST:
                method = std::string(hm->method.p,hm->method.len) ;
                boost::to_lower(method);
                url =std::string (hm->uri.p,hm->uri.len);
                Application::instance()->getLogger().debug(url);
                start = std::time(NULL);
                if (mg_vcmp(&hm->uri, "/ctp/settings") == 0) {
                } else if (mg_vcmp(&hm->uri, "/ctp/account") == 0) { // 查询资金账户
                    http->handle_account_query(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/ctp/position/list") == 0) { // 持仓记录
                    http->handle_postion_query(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/ctp/order/list") == 0) { // 委托记录
                    http->handle_order_query(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/ctp/trade/list") == 0) { // 委托记录
                    http->handle_trade_query(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/ctp/order/send") == 0) { // 委托
                    http->handle_order_send(nc, hm);

//                    if (method == std::string("post")) { // 注册
//                        http->handle_innerdevice_register(nc, hm);
//                    } else if (method == "delete") { // 注销
//                    http->handle_innerdevice_remove(nc, hm);
//                    }
                } else if (mg_vcmp(&hm->uri, "/ctp/order/cancel") == 0) { // 撤单
                    http->handle_order_cancel(nc, hm);

                } else if (mg_vcmp(&hm->uri, "/ctp/instrument/detail") == 0) { // 查询合约信息 （ 手续费、保证金 ...）
                    http->handle_instrument_get(nc, hm);
                } else if (mg_vcmp(&hm->uri, "/ctp/instrument/query") == 0) { // 执行一次合约查询 （ 手续费、保证金 ...）
                    http->handle_instrument_query(nc, hm);
                } else {
                    mg_serve_http(nc, hm, s_http_server_opts); /* Serve static content */
                }

                end = std::time(NULL);

                ss << "It Costed " << (end-start) << " Seconds."<< std::endl;
                Application::instance()->getLogger().debug(ss.str());
                break;
            default:
                break;
        }
    }catch (boost::bad_lexical_cast& e){
        send_http_response_error(nc,Error_ParameterInvalid);
    }
}

void HttpService::thread_run() {
	
	
	running_ = true;
	while( running_ ){
		mg_mgr_poll(&mgr, 1000);
	}
	mg_mgr_free(&mgr);
	
}

bool  HttpService::init(const Config& cfgs){
	cfgs_ = cfgs;
	return true;
}

bool HttpService::open(){
	
	int i;
	char *cp;
	const char *err_str;
    struct mg_connection *nc;
	mg_mgr_init(&mgr, NULL);
	s_http_server_opts.document_root = "/tmp/smartbox/http";
	std::string http_port  = cfgs_.get_string("http.port","8000");
	
//	std::function< void (struct mg_connection *, int , void *) >  fx =std::bind( &HttpService::ev_handler,_1,_2,_3);
//	auto  fx =std::bind( &HttpService::ev_handler,_1,_2,_3);
	
//
//	nc = mg_bind_opt(&mgr, s_http_port,std::bind(&HttpService::ev_handler,this,_1,_2,_3), bind_opts);
	nc = mg_bind_opt(&mgr, http_port.c_str(),HttpService::ev_handler, bind_opts);
//	nc = mg_bind_opt(&mgr, s_http_port,(mg_event_handler_t)fx, bind_opts);
	if (nc == NULL) {
//		fprintf(stderr, "Error starting server on port %s: %s\n", http_port.c_str(),*bind_opts.error_string);
		fprintf(stderr, "Error starting server on port %s\n", http_port.c_str());
		return false;
	}
	Application::instance()->getLogger().info("starting http server on port :" + http_port);
	mg_set_protocol_http_websocket(nc);
	s_http_server_opts.enable_directory_listing = "yes";
	
	printf("Starting RESTful server on port %s, serving %s\n", http_port.c_str(),
	       s_http_server_opts.document_root);
	thread_ = std::make_shared<std::thread>( std::bind(&HttpService::thread_run,this));
	
	return true;
}

void HttpService::close(){
	running_ = false;
	thread_->join();
}

void HttpService::run() {
//	thread_->join();
}

// 向外 http 连接请求返回处理入口
void ev_connect_handler(struct mg_connection *nc, int ev, void *ev_data) {

    std::string name = (char*) nc->user_data;
    HttpService* http = HttpService::instance().get();

    if (ev == MG_EV_HTTP_REPLY) { // 服务器返回
        struct http_message *hm = (struct http_message *)ev_data;
        nc->flags |= MG_F_CLOSE_IMMEDIATELY;


        Json::Reader reader;
        Json::Value root;
        std::string json(hm->body.p,hm->body.len);
        Application::instance()->getLogger().debug("Http Response:" + json);
        if (reader.parse(json, root)){
            if( root.get("status",Json::Value("0")).asInt() != 0){
                // error
                return ;
            }
        }else{
            Application::instance()->getLogger().debug("Http Response Data Parse Error");
            return ;
        }

//        InnerController::instance()->onHttpResult(name,root);

    } else if (ev == MG_EV_CLOSE) {
//        exit_flag = 1;
    };

}


void HttpService::http_request(const std::string& url, const PropertyStringMap& headers, const PropertyStringMap& vars,
                  void* user_data){
    struct mg_connection *nc;

    //处理http header
    std::string head_text ;
    for(auto p:headers) {
        boost::format fmt("%s: %s\r\n");
        fmt % p.first.c_str() % p.second.c_str();
        head_text +=  fmt.str();
    }
    if(head_text.length() == 0){
        head_text = "Content-Type: application/x-www-form-urlencoded\r\n";
    }

    // 处理post 参数
    std::string var_text ;
    for(auto p:vars) {
        std::string key ,value;
        key = p.first;
        value = p.second;
        mg_str k = mg_mk_str(key.c_str());
        mg_str v = mg_mk_str(value.c_str());

        k = mg_url_encode(k);
        v = mg_url_encode(v);
        key = std::string(k.p,k.len);
        value = std::string(v.p,v.len);

        free((void*)k.p);
        free((void*)v.p);

        if( var_text.length()){
            var_text +=  "&";
        }
        var_text += key + "=" + value;
    }
    if( var_text.length()) {
        nc = mg_connect_http(&mgr, ev_connect_handler,url.c_str(), head_text.c_str(), var_text.c_str());
    }else{
        nc = mg_connect_http(&mgr, ev_connect_handler,url.c_str(), head_text.c_str(), NULL);
    }
    nc->user_data = user_data;

}

//查询设备运行状态
// 1.1
void HttpService::handle_account_query(struct mg_connection *nc, struct http_message *hm ){
    Json::Value data = defaultResponseJsonData();
    data["result"] = TdApi::instance().getAccountInfo();
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}


void HttpService::handle_postion_query(struct mg_connection *nc, struct http_message *hm ){
    Json::Value data = defaultResponseJsonData();
    data["result"] = TdApi::instance().getPositions();
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

void HttpService::handle_order_query(struct mg_connection *nc, struct http_message *hm ){
    Json::Value data = defaultResponseJsonData();

    std::string user_no = http_get_query_var(hm,"user_no");
    std::string trans_no = http_get_query_var(hm,"trans_no");

    data["result"] = TdApi::instance().getOrders(user_no,trans_no);
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

void HttpService::handle_trade_query(struct mg_connection *nc, struct http_message *hm ){
    Json::Value data = defaultResponseJsonData();
    data["result"] = TdApi::instance().getTradeRecords();
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

void HttpService::handle_order_send(struct mg_connection *nc, struct http_message *hm ){
    OrderRequest  req;
    req.cc = THOST_FTDC_CC_Immediately;
    req.tc = THOST_FTDC_TC_IOC;
    req.vc = THOST_FTDC_VC_CV;

    req.symbol = http_get_var(hm,"instrument");
    req.price = boost::lexical_cast<float>(http_get_var(hm,"price"));
    req.volume = boost::lexical_cast<int>(http_get_var(hm,"volume"));
    req.direction = THOST_FTDC_D_Buy;
    req.offset = std::string(1,THOST_FTDC_OFEN_Open);
    req.price_type = THOST_FTDC_OPT_LimitPrice;
    std::string value = http_get_var(hm,"price_type");
    if(value.size()){
        req.price_type = value[0];
    }

    std::string direction,oc ;
    direction = boost::lexical_cast<std::string>(http_get_var(hm,"direction"));
    oc = boost::lexical_cast<std::string>(http_get_var(hm,"oc"));
    if(direction == "sell"){
        req.direction = THOST_FTDC_D_Sell;
    }
    if( oc == "close"){
        req.offset = std::string(1,THOST_FTDC_OFEN_Close);
    }
    if( oc == "forceclose"){
        req.offset = std::string(1,THOST_FTDC_OFEN_ForceClose);
    }
    if( oc == "closetoday"){
        req.offset = std::string(1,THOST_FTDC_OFEN_CloseToday);
    }
    if( oc == "closeyesterday"){
        req.offset = std::string(1,THOST_FTDC_OFEN_CloseYesterday);
    }

    req.exchange_id = http_get_var(hm,"exchange_id");

    value = http_get_var(hm,"cc");
    if(value.size()){
        req.cc = value[0];
    }
    value = http_get_var(hm,"tc");
    if(value.size()){
        req.tc = value[0];
    }
    value = http_get_var(hm,"vc");
    if(value.size()){
        req.vc = value[0];
    }


    Json::Value data = defaultResponseJsonData();
    data["result"] = TdApi::instance().sendOrder(req);
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

//撤单

/*
     *  UserOrderId : A-FrontID-SessionID-OrderRef
     *  SysOrderId : B-ExchangeID-OrderSysID
     * */
void HttpService::handle_order_cancel(struct mg_connection *nc, struct http_message *hm ){
    std::string instrument , exchange ,order_sys_id , order_id;
    order_id = http_get_var(hm,"order_id"); // ExchangeID + OrderSysID  (szf.12212)


    std::vector< std::string > fields;
    boost::split(fields,order_id,boost::is_any_of("#"));
    if( fields.size() < 3){
        send_http_response_error(nc,Error_ParameterInvalid,"order_id invalid");
        return ;
    }
    CancelOrderRequest req;

    std::string a,b,c,d;
    a = fields[0];
    b = fields[1];
    c = fields[2];
    if( fields.size() > 3){
        d = fields[3];
    }
    if( a == "A"){
        req.front_id = boost::lexical_cast<int>(b);
        req.session_id = boost::lexical_cast<int>(c);
        req.order_ref = d;
    }else if( a == "B"){
        req.exchange = b;
        req.order_sys_id = c;
    }else{
        send_http_response_error(nc,Error_ParameterInvalid,"order_id invalid");
        return ;
    }


    Json::Value data = defaultResponseJsonData();
    data["result"] = TdApi::instance().cancelOrder(req);
//    std::string text = data.toStyledString();
    send_http_response_result( data, nc);
}

//查询合约相关信息
void HttpService::handle_instrument_get(struct mg_connection *nc, struct http_message *hm ){
    std::string instrument ;
    instrument = http_get_query_var(hm,"instrument");

    Json::Value data = defaultResponseJsonData();
    data["result"] = TdApi::instance().getInstrumentInfo(instrument);
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

//查询合约相关信息
void HttpService::handle_instrument_query(struct mg_connection *nc, struct http_message *hm ){
    std::string instrument ;
    if( TdApi::instance().isLogin() == false){
        send_http_response_error(nc,Error_UserNotLogin,"Error_UserNotLogin");
        return ;
    }
    instrument = http_get_query_var(hm,"instrument");
    if(instrument.size() == 0){
        instrument = http_get_var(hm,"instrument");
    }

    Json::Value data = defaultResponseJsonData();
    data["result"] = TdApi::instance().queryInstrumentInfo(instrument);
    std::string text = data.toStyledString();
    send_http_response(nc,text,defaultResponseHeaders());
}

