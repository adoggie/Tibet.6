//
// Created by bin zhang on 2019/2/9.
//

#include "error.h"

ErrorDefineTable_t ErrorDefs ={
		{Error_NoError,"no error"},
		{Error_UnknownError,"unknown error"},
		{Error_SystemFault,"Error_SystemFault"},
		{Error_TokenInvalid,"Error_TokenInvalid"},
		{Error_AccessDenied,"Error_AccessDenied"},
		{Error_PermissionDenied,"Error_PermissionDenied"},
		{Error_ParameterInvalid,"Error_ParameterInvalid"},
		{Error_PasswordError,"Error_PasswordError"},
		{Error_UserNotExist,"Error_UserNotExist"},
		{Error_ObjectHasExist,"Error_ObjectHasExist"},
		{Error_ObjectNotExist,"Error_ObjectNotExist"},
		{Error_ResExpired,"Error_ResExpired"},
		{Error_ReachLimit,"Error_ReachLimit"},

		{Error_UserNotLogin,"Error_UserNotLogin"},

};