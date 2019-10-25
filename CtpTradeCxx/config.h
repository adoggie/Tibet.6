//
// Created by bin zhang on 2019/1/6.
//

#ifndef INNERPROC_CONFIG_H
#define INNERPROC_CONFIG_H

#include "base.h"


class Config{
	PropertyStringMap props_;
public:
	long get_long(const std::string& name,long def=0) const;
	int get_int(const std::string& name,int def=0) const;
	int get_float(const std::string& name,float def=0.) const;
	std::string get_string(const std::string& name,const std::string& def="") const;
	bool get_bool(const std::string& name,bool def=false) const;
	
	void load(const std::string& filename);
	void save(const std::string& filename);
	
	void set_int(const std::string& name,int value);
	void set_float(const std::string& name,float value);
	void set_string(const std::string& name,const std::string& value);
	void set_bool(const std::string& name,bool value);

	void update(const Config& cfgs);
	void clear();
};



//class DeviceRegisterTable:public Object{
////	PropertyStringMap _props;
//	std::vector<RegDeviceInfo> devices_;
//public:
//	std::vector<RegDeviceInfo>& devices(){ return devices_;}
//	void load(const std::string& filename);
//	void save(const std::string& filename);
//};


#endif //INNERPROC_CONFIG_H
