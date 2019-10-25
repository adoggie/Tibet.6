#ifndef INNERPROC_HTTP_API_H
#define INNERPROC_HTTP_API_H

#include "base.h"
#include <jsoncpp/json/json.h>

struct BoxStatusInfo{
	std::time_t     time;
	std::string     ver;
	std::uint32_t   fds;
	std::uint32_t   threads;
	std::uint32_t   mem_rss;
//	std::uint32_t  mem_free;
//	std::uint32_t  disk_free;
	int             outbox_net;          //是否与室外机连接正常 0: offline , n: 最近此次活跃时间戳
	int             propserver_net;      //是否与物业服务器连接正常 0: offline , n: 最近此次活跃时间戳
	std::string     net_ip;      // 小区网ip
	std::uint16_t   net_call_port;
	
	std::string     family_ip;   // 家庭内网ip
	std::uint16_t   family_call_port;
	
	std::string     propserver_url; //物业服务http接⼝地址,转发到物业服务器
	int             alarm_enable;       // 启用报警 0: 关闭 , 1: 启用
    int             watchdog_enable;    // 启⽤看⻔狗
    int             call_in_enable;     //是否禁⽌呼叫进⼊ 0: 禁⽌呼⼊ ， 1：允许呼⼊
	int             seczone_mode;       //当前防区mode编号
	Json::Value values();
};


struct BoxDiscoverInfo{
	std::time_t  time;
	std::string  ver;
	std::string  service_api;
	std::string  server_api;
	std::string  push_address;
};


#define HTTP_JSON_RESULT_STATUS_OK 0
#define HTTP_JSON_RESULT_STATUS_ERROR 1




#endif