#!/bin/bash
####usage: proxy-balance.sh localhost:18087 2

######## $1 dashboard address ######
if [ -z $1 ];then
   exit 1;
fi

######## $2 connections ratio ######
if [ -z $2 ];then
   exit 1;
fi

average=0; result=0

function getaverage(){
    num=0; total=0
    for p in `curl -s $1/api/proxy/list |grep \"id\" |awk -F: '{print $2}' |awk -F, '{print $1}' |awk -F\" '{print $2}'`
    do
        conn=$(ssh -p 3299 easemob@$p "/usr/sbin/ss -ant |grep 19000 |wc -l")
        total=$((total+conn))
        num=$((num+1))
    done
    average=$((total/num))
}

function checkratio(){
    if [ $1 -gt $2 ];then
        rate=$(($1/$2))
        if [ $rate -gt $3 ];then
            echo $4:connection number is abnormal
            result=1
        fi
    else
        rate=$(($2/$1))
        if [ $rate -gt $3 ];then
            echo $4:connection number is abnormal
            result=1
        fi
    fi
}

function getratio(){
    for p in `curl -s $1/api/proxy/list |grep \"id\" |awk -F: '{print $2}' |awk -F, '{print $1}' |awk -F\" '{print $2}'`
    do
        conn=$(ssh -p 3299 easemob@$p "/usr/sbin/ss -ant |grep 19000 |wc -l")
        checkratio $conn $average $2 $p
    done
    echo $result
}

function main(){
    getaverage $1
    getratio $1 $2
}

main $1 $2
