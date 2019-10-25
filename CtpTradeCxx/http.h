//
// Created by bin zhang on 2019/1/6.
//

#ifndef INNERPROC_HTTP_H
#define INNERPROC_HTTP_H

#include <thread>
#include <atomic>
#include "base.h"
#include "service.h"
#include "mongoose.h"

#include <jsoncpp/json/json.h>

#define HTTP_JSON_RESULT_STATUS_OK 0
#define HTTP_JSON_RESULT_STATUS_ERROR 1


struct HttpRequest{
	std::string url;
	PropertyMap head;
	std::string method;
	std::string content;
};

struct HttpResponse{

};

typedef std::map< std::string, std::string> HttpHeaders_t;

class HttpService:Service{

public:
	static std::shared_ptr<HttpService>& instance(){
		static std::shared_ptr<HttpService> handle ;
		if(!handle.get()){
			handle = std::make_shared<HttpService>() ;
		}
		return handle;
	}
	
	bool  init(const Config& cfgs);
	
	bool open();
	void close();
	void run();
public:
	static void ev_handler(struct mg_connection *nc, int ev, void *ev_data);
	void handle_innerdevice_register(struct mg_connection *nc, struct http_message *hm );

	void handle_account_query(struct mg_connection *nc, struct http_message *hm );
	void handle_postion_query(struct mg_connection *nc, struct http_message *hm );
	void handle_order_query(struct mg_connection *nc, struct http_message *hm );
	void handle_trade_query(struct mg_connection *nc, struct http_message *hm );
	void handle_order_send(struct mg_connection *nc, struct http_message *hm );
	void handle_order_cancel(struct mg_connection *nc, struct http_message *hm );
	void handle_instrument_query(struct mg_connection *nc, struct http_message *hm ); //查询合约相关信息
	void handle_instrument_get(struct mg_connection *nc, struct http_message *hm ); //查询合约相关信息



    // 发送 HTTp 请求
    void http_request(const std::string& url, const PropertyStringMap& headers, const PropertyStringMap& vars,
                      void* user_data);

//    void ev_connect_handler(struct mg_connection *nc, int ev, void *ev_data);

	bool check_auth(struct mg_connection *nc,struct http_message *hm ,const std::string& code="token" );
	
	void thread_run();

    void handle_resp_init_data(Json::Value& root );

private:
	Config 	cfgs_;
//	std::shared_ptr<std::thread> thread_;
	std::atomic_bool running_;
	
};

//class InnerServiceHandler:HttpHandler{
//
//	void onRequest(const std::shared_ptr<HttpRequest>& req,std::shared_ptr<HttpResponse>& resp);
//
//};



#endif //INNERPROC_HTTP_H
