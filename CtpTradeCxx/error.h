//
// Created by bin zhang on 2019/2/9.
//

#ifndef INNERPROC_ERROR_H
#define INNERPROC_ERROR_H

#include "base.h"
typedef  std::map< int , std::string > ErrorDefineTable_t;


#define Error_NoError 0
#define Error_UnknownError 1	// 未定义

#define Error_SystemFault 1001	// 系统错误
#define Error_TokenInvalid 1002	// 令牌错误
#define Error_AccessDenied 1003	// 访问受限
#define Error_PermissionDenied 1004	// 权限受限
#define Error_ParameterInvalid 1005	// 参数无效
#define Error_PasswordError 1006	// 密码错误
#define Error_UserNotExist 1007		// 用户不存在
#define Error_ObjectHasExist 1008	// 对象已存在
#define Error_ObjectNotExist 1009	// 对象不存在
#define Error_ResExpired 1010		// 资源过期
#define Error_ReachLimit 1011	 	// 达到上限


#define Error_UserNotLogin 2001	 	// 用户未登录


extern  ErrorDefineTable_t ErrorDefs;

#endif //INNERPROC_ERROR_H
