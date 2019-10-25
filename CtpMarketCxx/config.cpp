//
// Created by bin zhang on 2019/1/6.
//

#include "config.h"
#include <string>
#include <fstream>
#include <iostream>
#include <boost/lexical_cast.hpp>
#include <stdexcept>

long Config::get_long(const std::string& name,long def) const{
	return def ;
}

int Config::get_int(const std::string& name,int def) const{
	auto result = def;
	try {
		auto value = props_.at(name);
		result = boost::lexical_cast<int>(value);
	}catch (...){

	}
	return result ;
}

std::string Config::get_string(const std::string& name,const std::string& def) const{
	auto result = def;
	try {
		auto value = props_.at(name);
		result = boost::lexical_cast<std::string>(value);
	}catch (...){

	}
	return result ;
}

bool Config::get_bool(const std::string& name,bool def) const{
	return def ;
}

void Config::load(const std::string& filename){
	std::ifstream file(filename);

	if (file.is_open())
	{
		std::string line;
		props_.clear();
		while(std::getline(file, line)){
			line.erase(std::remove_if(line.begin(), line.end(), isspace), line.end());
			if(line[0] == '#' || line.empty())
				continue;
			auto delimiterPos = line.find("=");
			auto name = line.substr(0, delimiterPos);
			auto value = line.substr(delimiterPos + 1);
			std::cout << name << " " << value << '\n';
			props_[name] = value;
		}
	}
	else {
		std::cerr << "["<< filename << "] Couldn't open config file for reading.\n";
	}
}

void Config::save(const std::string& filename){
	std::ofstream os(filename);
	for(auto p : props_){
		os<<p.first<<" = " << p.second << std::endl;
	}
	os.close();
}

void Config::update(const Config& cfgs){
	for(auto p:cfgs.props_){
		props_[p.first] = p.second;
	}
}


void Config::set_int(const std::string& name,int value){
	props_[name] = boost::lexical_cast<std::string>(value);
}

void Config::set_float(const std::string& name,float value){
	props_[name] = boost::lexical_cast<std::string>(value);
}

void Config::set_string(const std::string& name,const std::string& value){
	props_[name] = boost::lexical_cast<std::string>(value);
}

void Config::set_bool(const std::string& name,bool value){
	props_[name] = boost::lexical_cast<std::string>(value);
}

void Config::clear(){
	props_.clear();
}