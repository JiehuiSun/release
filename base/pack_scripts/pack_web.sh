#!/bin/bash

echo "接收的参数为：$1"

BUILD_ENV_TYPE=$1          #test/pre/pro
#BUILD_PROJECT_NAME=$2      #项目文件名


#***************web build start****************#
#build
npm config set registry=http://op-npm.mumway.com
npm i --save --unsafe-perm  
npm run build:${BUILD_ENV_TYPE}

if [[ $? = 0 ]];then
echo "********* 构建成功 ********"
else
echo "********* 构建失败 *********"
exit 0
fi
#***************web build end****************#
