#!/usr/bin/env python
#coding=utf-8

# example ./appSessionReset.py localhost

import urllib
import urllib2
import json
import sys
import redis
import time
import threading
import binascii


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

######session user online
def sessionUserFromCodisSlave(codisAddr):
    dict = {}
    slaves = getCodisSlave(codisAddr+":18087")
    total = 0
    #get data
    for s in slaves:
        host = s.strip('\"').split(':')[0].strip()
        port = int(s.strip('\"').split(':')[1].strip())
        rd = redis.Redis(host, port, 0)
        keys = rd.keys("*")
        total += len(keys)
        for k in keys:
            if (k.find('_') > -1):
                app = k.split('_')[0]
                if app in dict:
                    dict[app] +=1
                else:
                   dict[app] = 1           
    # reste and store data
    ntp = int(time.time())
    dtp = ntp - ntp % 86400
    out = open("appSession.data", 'w')
    rd = redis.Redis(codisAddr, 19000, 0)
    for k in dict:
        rd.hset(k, "current", dict[k])
        rd.hset(k, "today", dict[k])
        rd.hset(k,"yesterday", dict[k])
        rd.hset(k, "week", dict[k])
        rd.hset(k, "month", dict[k])
        rd.hset(k, "timestamp", dtp)
        out.write(k+' '+str(dict[k])+'\n')
    out.close()
    print(total)


if __name__ == '__main__':
    print("Begin:")
    sessionUserFromCodisSlave(sys.argv[1])
    print("End")

