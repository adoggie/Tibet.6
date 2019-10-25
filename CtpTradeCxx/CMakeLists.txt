cmake_minimum_required(VERSION 2.8)
project(CtpTradeCxx)

set(CMAKE_CXX_STANDARD 11)

set(Boost_USE_MULTITHREADED      ON)

option(zsqh_test "zsqh_test" OFF)
option(zsqh_prd "zsqh_prd" OFF)
option(simnow "simnow" ON)
#option(simnow ON)

#find_package(Boost 1.59.0 COMPONENTS python thread date_time system chrono REQUIRED)
link_directories( /usr/local/lib   )
#link_directories("/usr/local/lib"   )


if(simnow)
    add_definitions(-D_CHUANTOU)
    include_directories(/usr/local/include ../CTP/simnow/v6.3.15)
    link_libraries(  boost_system boost_thread boost_date_time  thosttraderapi_se_simnow pthread jsoncpp  hiredis redis++)
    add_executable(CtpTrade-simnow tradeImpl.cpp tradeImpl.h trade.cpp trade.h main.cpp
            app.cpp config.cpp logger.cpp service.cpp
            http.h http.cpp mongoose.h mongoose.c
            error.h error.cpp http-api.h
            )
endif()

if(zsqh_test)
    add_definitions(-D_CHUANTOU)
    include_directories(/usr/local/include ../CTP/zsqh/test/6.3.13)
    link_libraries(  boost_system boost_thread boost_date_time  thosttraderapi_se_zsqh_test pthread jsoncpp hiredis redis++)
    add_executable(CtpTrade-zsqh-test tradeImpl.cpp tradeImpl.h trade.cpp trade.h main.cpp
            app.cpp config.cpp logger.cpp service.cpp
            http.h http.cpp mongoose.h mongoose.c
            error.h error.cpp http-api.h
            )
endif()

if(zsqh_prd)
    add_definitions(-D_CHUANTOU -D_ZSQH_PRD)
    include_directories(/usr/local/include ../CTP/zsqh/product/6.3.15)
    link_libraries(  boost_system boost_thread boost_date_time  thosttraderapi_se_zsqh_prd pthread jsoncpp hiredis redis++)
    add_executable(CtpTrade-zsqh-prd tradeImpl.cpp tradeImpl.h trade.cpp trade.h main.cpp
            app.cpp config.cpp logger.cpp service.cpp
            http.h http.cpp mongoose.h mongoose.c
            error.h error.cpp http-api.h
            )
endif()
