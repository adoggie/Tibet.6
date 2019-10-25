//
// Created by bin zhang on 2019/1/6.
//

#ifndef INNERPROC_LOGGER_H
#define INNERPROC_LOGGER_H


#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>


#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <list>
#include <deque>
#include <fstream>

#include <boost/shared_ptr.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/format.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>


using namespace boost::gregorian;
using namespace boost::posix_time;

class Logger;
typedef boost::shared_ptr<Logger> LoggerPtr;

class Logger{
public:
	Logger(){
		_level = Types ::INFO;
	}
	
	~Logger(){
		//flush();
	}
	
	static LoggerPtr create(){
		return LoggerPtr(new Logger);
	}
	
	enum Types{
		FATAL,
		ALERT,
		CRIT,
		ERROR,
		WARN,
		INFO,
		DEBUG,
		
	};
	class Handler{
	public:
		virtual ~Handler(){};
		virtual void write(const std::string& log,Types type =INFO )=0;
		virtual void flush()=0; //异步写入
	};
	typedef std::shared_ptr<Handler> HandlerPtr;
	
	
	Logger& setLevel(Types level){
		_level = level;
		return *this;
	}
	
	Logger& addHandler(HandlerPtr h){
		_handlers.push_back(h);
		return *this;
	}
	
	//需要外部驱动执行
	void flush(){
		std::vector<HandlerPtr>::iterator itr;
		for(itr=_handlers.begin();itr!=_handlers.end();itr++){
			(*itr)->flush();
		}
	}
	
	void write(const std::string& log,Types type){
		std::vector<HandlerPtr>::iterator itr;
		if(_level <  type){
			return; // 忽略
		}
		ptime curtime = second_clock::local_time();
//		to_simple_string
		tm t = to_tm(curtime);
		
		boost::format fmt1 = boost::format("%04d-%02d-%02d %02d:%02d:%02d");
		fmt1%(t.tm_year+1900)%t.tm_mon%t.tm_mday%t.tm_hour%t.tm_min%t.tm_sec;
		
		std::string timestr =  fmt1.str();
		std::string level = "DEBUG";
		switch ( int(type) ){
			case INFO: level = "INFO";break;
			case WARN: level = "WARN";break;
			case ERROR: level = "ERROR";break;
			case CRIT: level = "CRIT";break;
			case DEBUG: level = "DEBUG";break;
		}
		
		boost::format fmt2("%1% %2% %3%");
		fmt2%timestr%level%log;
		std::string text = fmt2.str() ;
		
		for(itr=_handlers.begin();itr!=_handlers.end();itr++){
			(*itr)->write(text,type);
		}
	}
	
	void debug(const std::string& log){
		write(log,Logger::Types::DEBUG);
	}
	
	void info(const std::string& log){
		write(log,Logger::Types::INFO);
	}
	
	void warn(const std::string& log){
		write(log,Logger::Types::WARN);
	}
	
	void error(const std::string& log){
		write(log,Logger::Types::ERROR);
	}
	
private:
	std::vector<HandlerPtr> _handlers;
	boost::mutex _mtx;
	Types _level;
};


class LogFileHandler:public Logger::Handler {
private:
	std::string 	logfile_;
	std::ofstream 	ostream_;
	date 			today_ ;
public:
	LogFileHandler(const std::string& logfile,std::uint32_t max_size=2^10*64){
		logfile_ = logfile;
	}
	
	~LogFileHandler(){
//		ostream_->close();
	}
	
	void write(const std::string &log, Logger::Types type = Logger::INFO){
		date nowday = day_clock::local_day();
		if(nowday != today_){
			
			today_ = nowday;
			time_t now = time(NULL);
			tm* now_tm = std::gmtime(&now);
			boost::format fmt("%s_%04d-%02d-%02d.log");
			fmt%logfile_.c_str()%(now_tm->tm_year+1900)%now_tm->tm_mon%now_tm->tm_mday;
			logfile_ = fmt.str();
			
		}
		
//		ostream_ = std::make_shared<std::ofstream>(this->logfile_.c_str(), std::ios::app);
		ostream_.open(this->logfile_, std::ios::app);
		ostream_<<log<<std::endl;
	}
	
	void flush(){
		ostream_.flush();
	}
	
	
};

class LogStdoutHandler:public Logger::Handler {
private:

public:
	LogStdoutHandler(){
	
	}
	
	~LogStdoutHandler(){
	
	}
	
	void write(const std::string &log, Logger::Types type = Logger::INFO){
		std::cout<<"\u001b[31m" <<log<<std::endl;
	}
	
	void flush(){
	
	}
	
};


/**
 * 模拟接收日志
 * nc -ul 9906
 *
 * */

class LogUdpHandler:public Logger::Handler {
	int sock_ ;
	std::string target_host_;
	unsigned  short target_port_;
	struct sockaddr_in addr_;

public:
	LogUdpHandler(const std::string& host, uint16_t port){
		sock_ = 0 ;
		target_host_ = host;
		target_port_ = port;
	}

	~LogUdpHandler(){
		if(sock_){
			close(sock_);
		}
	}

	void write(const std::string &log, Logger::Types type = Logger::INFO){
		if(sock_ == 0){
			if ((sock_ = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
				return;
			}
			bzero(&addr_, sizeof(addr_));
			addr_.sin_family = AF_INET;
			addr_.sin_port = htons( target_port_ );
			addr_.sin_addr.s_addr = inet_addr( target_host_.c_str());
		}
		int addr_len = sizeof(struct sockaddr_in);

		sendto(sock_, (log+"\n").c_str(), log.size(), 0, (struct sockaddr *)&addr_, addr_len);
	}

	void flush(){

	}

};


#define log_log(logger,FMT,LEVEL,args...)  	{ \
							std::string sfmt = FMT + std::string("%s");\
							boost::format fmt(sfmt );\
							fmt args  %"";\
							logger->write(fmt.str(),LEVEL);\
							}
#define log_debug(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::DEBUG,args)
#define log_info(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::INFO,args)
#define log_warn(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::WARN,args)
#define log_error(logger,FMT,args...)  	log_log(logger,FMT,tce::Logger::ERROR,args)



#endif //INNERPROC_LOGGER_H


/**
http://codingnow.cn/language/1224.html
 https://www.cnblogs.com/lidabo/p/3938969.html
 */