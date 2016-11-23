#!/usr/bin/env python
#coding=utf-8

import urllib
import urllib2
import json
import sys
import redis
import binascii

####usage####
#python bigKeysFromCodisSlave.py localhost:6379

######keys all codis slave datas
def bigKeysGetFromRedisServer(redisAddr):
    out = open(redisAddr+"-large1wKeys.data", 'w')
    host = redisAddr.strip('\"').split(':')[0].strip()
    port = int(redisAddr.strip('\"').split(':')[1].strip())
    print(redisAddr+' start')
    rd = redis.Redis(host, port, 0)
    keys = rd.keys("*")
    total += len(keys)
    for k in keys:
        type = rd.type(k)
        klen = 0
        if type == 'hash':
            klen = rd.hlen(k)
            if klen > 10000:
                keys1w +=1
                out.write(str(type)+' '+str(k)+' '+str(klen)+'\n')
        elif type == 'list': 
            klen = rd.llen(k)
            if klen > 10000:
                keys1w +=1
                out.write(str(type)+' '+str(k)+' '+str(klen)+'\n')
        elif type == 'set': 
            klen = rd.scard(k)
            if klen > 10000:
                keys1w +=1
                out.write(str(type)+' '+str(k)+' '+str(klen)+'\n')
        elif type == 'zset': 
            klen = rd.zcard(k)
            if klen > 10000:
                keys1w +=1
                out.write(str(type)+' '+str(k)+' '+str(klen)+'\n')
        else:
            continue
        #print(type+' '+k+' '+str(klen))
    print(redisAddr+' finished')
    out.close()
    print(total)
    print(keys1w)

if __name__ == '__main__':
    bigKeysGetFromRedisServer(sys.argv[1])

