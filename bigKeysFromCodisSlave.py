#!/usr/bin/env python
#coding=utf-8

import urllib
import urllib2
import json
import sys
import redis
import binascii

####usage####
#python bigKeysFromCodisSlave.py localhost:18087

####################codis api
def getCodisInfo(codisAddr, path):
    tmUrl = 'http://'+codisAddr+path
    header = {"Content-Type": "application/json"}
    request = urllib2.Request(tmUrl,  headers = header)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        print (' Get all teams HTTPError:'+str(e.code)+'\n')
        return -1
    except urllib2.URLError, e:
        print (' Get all teams URLError:'+e.reason+'\n')
        return -1
    else:
        jRes = json.loads(response.read())
        return jRes


####################codis info
def getCodisSlave(codisAddr):
    server_groups = getCodisInfo(codisAddr,"/api/server_groups")
    slaveList = []
    for s in server_groups:
        servers = s["servers"]
        for h in servers:
            if h["type"] == "slave":
                slaveList.append(json.dumps(h["addr"]))
    return slaveList

######keys all codis slave datas
def bigKeysGetFromCodisSlave(codisAddr):
    out = open(codisAddr+"-large1wKeys.data", 'w')
    slaves = getCodisSlave(codisAddr)
    total = keys1w = 0
    for s in slaves:
        host = s.strip('\"').split(':')[0].strip()
        port = int(s.strip('\"').split(':')[1].strip())
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
        print(s+' finished')
    out.close()
    print(total)
    print(keys1w)

if __name__ == '__main__':
    bigKeysGetFromCodisSlave(sys.argv[1])

