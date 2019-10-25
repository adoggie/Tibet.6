#code:utf-8

import json

def response_data_json(fx):
    def _wrapped(*args,**kwargs):
        # {'code': code, 'errmsg': cs.ERR_MSG[code], 'data': rval})
        data = fx(*args,**kwargs)

    return _wrapped