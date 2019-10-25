//
// Created by bin zhang on 2019/1/6.
//

#ifndef INNERPROC_APP_H
#define INNERPROC_APP_H

#include "base.h"
#include "config.h"
#include "service.h"
#include "logger.h"


class Application:public Object,public ServiceContainer{
	Logger 	logger_;
	Config  cfgs_;
	boost::asio::io_service io_service_;
//	InnerController controller_;
	std::vector<std::shared_ptr<Service> > services_;
public:
	static std::shared_ptr<Application>& instance();

	Application&  init();

	Logger& getLogger();

	void run();
	void stop();
	boost::asio::io_service&  io_service() { return io_service_;}

	void addService(std::shared_ptr<Service>& service );

	Config& getConfig();
	
	std::string name();
protected:
	void wait_for_shutdown();

};



#endif //INNERPROC_APP_H
