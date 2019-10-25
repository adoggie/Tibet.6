cmake_minimum_required(VERSION 3.0)
project(CtpMarketCxx)

set(CMAKE_CXX_STANDARD 11)

option(zsqh_test "zsqh_test" OFF)
option(zsqh_prd "zsqh_prd" ON)
option(simnow "simnow" OFF)

set(Boost_USE_MULTITHREADED      ON)
#find_package(Boost 1.59.0 COMPONENTS  thread date_time system chrono REQUIRED)

link_directories(/usr/local/lib )


if(simnow)
    link_libraries( boost_system boost_thread boost_date_time thostmduserapi_se_simnow pthread hiredis redis++ jsoncpp )
#    include_directories(ctpapi/x64_linux)
    include_directories(../CTP/simnow/v6.3.15)
    add_executable(CtpMarket-simnow main.cpp market.cpp app.cpp config.cpp logger.cpp service.cpp)
endif()

if(zsqh_test)
    #穿透式接入
    add_definitions(-D_CHUANTOU)
    link_libraries( boost_system boost_thread boost_date_time thostmduserapi_se_zsqh_test pthread hiredis redis++ jsoncpp )
    include_directories(../CTP/zsqh/test/6.3.13)
    add_executable(CtpMarket-zsqh-test main.cpp market.cpp app.cpp config.cpp logger.cpp service.cpp)
endif()

if(zsqh_prd)
    add_definitions(-D_CHUANTOU -D_ZSQH_PRD)
    link_libraries( boost_system boost_thread boost_date_time thostmduserapi_se_zsqh_prd pthread hiredis redis++ jsoncpp )
    include_directories(../CTP/zsqh/product/6.3.15)
    add_executable(CtpMarket-zsqh-prd main.cpp market.cpp app.cpp config.cpp logger.cpp service.cpp)
endif()