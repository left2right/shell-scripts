#!/usr/bin/env python
#coding=utf-8

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

def allCodisDBSIZE(codisAddr):
    slaves = getCodisSlave(codisAddr)
    total = 0
    for s in slaves:
        host = s.strip('\"').split(':')[0].strip()
        port = int(s.strip('\"').split(':')[1].strip())
        rd = redis.Redis(host, port, 0)
        total += rd.dbsize()
    return total

######keys all codis slave datas
def keysNumGetFromCodisSlave(codisAddr, key):
    #out = open(key+"KeysFromCodisSlave.data", 'w')
    slaves = getCodisSlave(codisAddr)
    total = 0
    for s in slaves:
        host = s.strip('\"').split(':')[0].strip()
        port = int(s.strip('\"').split(':')[1].strip())
        rd = redis.Redis(host, port, 0)
        keys = rd.keys("*"+key+"*")
        num = len(keys)
        total += num
        #out.write(str(num)+'\n')
    return total
    #out.close()

if __name__ == '__main__':
    ## session datas
    sessionAll = allCodisDBSIZE("ebs-ali-beijing-codis51:18087")
    sessionApp = keysNumGetFromCodisSlave("ebs-ali-beijing-codis51:18087", sys.argv[1])
    sessionRatio = sessionApp/1.0/sessionAll
    print("Total connections:%d" %sessionAll)
    print("%s connections:%d" %(sys.argv[1],sessionApp))
    print("Connection ratio:%.3f" %(sessionRatio))
    ## message datas
    msgAll =  allCodisDBSIZE("ebs-ali-beijing-codis101:18087")
    msgApp = keysNumGetFromCodisSlave("ebs-ali-beijing-codis101:18087", sys.argv[1])
    msgRatio=msgApp/1.0/msgAll
    print("Total messages:%d" %msgAll)
    print("%s messages:%d" %(sys.argv[1],msgApp))
    print("Messages ratio:%.3f" %(msgRatio))
