#!/bin/bash

echo "接收的参数为：$1 $2"

BUILD_ENV_TYPE=$1          #test/pre/pro
BUILD_PROJECT_NAME=$2      #项目文件名



#***************php build start****************#
#build
base=$(cd `dirname $0`; pwd)
cd $base
cd ..
tar -cvf ${BUILD_PROJECT_NAME}.tar ${BUILD_PROJECT_NAME}/
