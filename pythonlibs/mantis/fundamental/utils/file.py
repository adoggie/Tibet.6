#coding:utf-8

import fcntl
import time

from lockfile import LockFile

def file_lock(filename):
    try:
        lock = LockFile(filename)
        lock.acquire(timeout=1)
    except:
        print 'lock failed'
        lock = None
    return lock

def file_unlock(lock):
    lock.release()

    # try:
    #     fp = open(filename,'w')
    #     ret = fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    #     # fp.close()
    #     if ret:
    #         return None
    # except IOError:
    #     return None
    #
    # return fp


if __name__ == '__main__':
    if file_lock('/tmp/aa'):
        print 'sleep 10s..'
        time.sleep(100)
