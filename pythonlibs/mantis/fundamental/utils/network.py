#coding: utf-8

import socket
def generate_range_address(host,start,end):
    return [(host,port) for port in range(start,end+1)]


def is_address_bindable(address,isTcp=True):
    """
    Test address,port has been binded.
    :param address: (host,port)
    :return:
    """
    if isTcp:
        isTcp = socket.SOCK_STREAM
    else:
        isTcp = socket.SOCK_DGRAM
    sock = socket.socket(type = isTcp)
    try:
        sock.bind(address)
    except:
        return False
    finally:
        sock.close()
    return True


def select_address_port(host,start,end,isTcp=True):
    """
    修正http侦听地址 ， 如果port未定义或者为0 ，则进行动态选定端口
    :param host: nic 地址
    :param start: 开始端口
    :param end: 结束端口
    :return: 可使用的地址
    """
    address_list = generate_range_address(host,start,end)
    for address in address_list:
        if is_address_bindable(address):
            return address
    return ()

if __name__ == '__main__':
    print generate_range_address('localhost',8000,8020)
    print is_address_bindable(('localhost',8000))
    print select_address_port('localhost',18001,18010)