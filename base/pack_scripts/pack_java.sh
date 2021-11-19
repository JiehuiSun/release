#!/bin/bash
# java

echo "接收的参数为：$1 $2"

BUILD_ENV_TYPE=$1          #test/pre/pro
BUILD_PROJECT_NAME=$2      #项目文件名
PACK_NAME=$3      #包名


mvn -U clean
mvn -U -Dmaven.test.skip=true -q compile package
mv $(echo "$(ls -d ./*server)")/target/*.jar ./ops_dev_path

# tar zcvf ../Release/javapack.tar.gz ordercenter-server.jar

if [[ $? = 0 ]];then
echo "********* 构建成功 ********"
else
echo "********* 构建失败 *********"
exit 0
fi
