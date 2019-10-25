//
// Created by bin zhang on 2019/1/6.
//

#ifndef INNERPROC_SERVICE_H
#define INNERPROC_SERVICE_H

#include <boost/asio.hpp>
#include "config.h"
#include <thread>


class Service{
protected:
	std::recursive_mutex 						mutex_;
	Config 					        cfgs_;
	boost::asio::io_service 		io_service_;
	boost::asio::deadline_timer 	timer_;
	std::shared_ptr<std::thread> 					thread_;
public:
	Service():timer_(io_service_){}
	virtual  ~Service(){};
public:
	virtual void lock(){};
	virtual void unlock(){};

public:
	virtual bool init(const Config& props) = 0;
	virtual bool open(){return false;};
	virtual void close(){
		io_service_.stop();
		thread_->join();
	};
	virtual void run(){
		thread_ = std::make_shared<std::thread>( std::bind(&Service::thread_run,this) );
	}

protected:
	virtual void thread_run(){
		io_service_.run();
	}
};


class  ListenService:Service{

};


struct ServiceContainer{
	virtual void addService(std::shared_ptr<Service>& service ) = 0;
};



//class HttpService: Service{
//public:
//	static std::shared_ptr<InnerDeviceManager>& instance(){
//		static std::shared_ptr<InnerDeviceManager> handle ;
//		if(!handle.get()){
//			handle = new InnerDeviceManager;
//		}
//	}
//
//	bool  init(const Config& cfgs){
//		cfgs_ = cfgs;
////		return shared_from_this();
//		return true;
//	}
//
//	void addHandler(const std::shared_ptr<HttpHandler> & handler);
//};
//
//





#endif //INNERPROC_SERVICE_H
