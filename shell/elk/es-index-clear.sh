#!/bin/bash
#删除ES中的index

#========== 配合jenkins使用，可做的批量删除
#ES_HOST=xxxx:9200  #ES地址
# #LIST_INDEXS  3_.monitoring 前面的3表示保留天数，下划线后面的用于模糊匹配
#LIST_INDEXS="
#3_.monitoring
#"
# #循环执行此脚本
#for es_index in $LIST_INDEXS
#do
#    ./es-index-clear.sh ${ES_HOST} ${es_index#*_} ${es_index%%_*} 'user:password'
#    sleep 3s
#done


#es的地址和端口
ES_HOST=$1
#要清理的索引起始部分
INDEX_START_WITH=$2
#保留天数
RERAIN_DAYS=$3
#登录信息
AUTH_INFO=$4

if [ ! -n "$ES_HOST" ] ;then
    echo "ES_HOST is not found, index is 1"
    exit 1
fi
if [ ! -n "$INDEX_START_WITH" ] ;then
    echo "INDEX_START_WITH is not found, index is 2"
    exit 1
fi
if [ ! -n "$RERAIN_DAYS" ] ;then
    echo "RERAIN_DAYS is not found, index is 3"
    exit 1
fi

if [ -n "$AUTH_INFO" ] ;then
    AUTH_INFO="-u ${AUTH_INFO}"
fi

echo "开始清理index数据 "`date "+%Y-%m-%d %H:%M:%S"`
echo "ES地址为                  ES_HOST=${ES_HOST}"
echo "需要清理的索引起始标记为   INDEX_START_WITH=${INDEX_START_WITH}"
echo "保留天数                  RERAIN_DAYS= ${RERAIN_DAYS}"
echo "=================================================================="

# 计算相差天数
function differDay(){
    a=`date --date="$1" +%s`
    b=`date --date="$2" +%s`
    c=`expr $a - $b`
    d=`expr "scale=0;$c / 3600 / 24"|bc`
    echo $d
}

# 开始删除
function delete_indices() {
    DATA_NOW=`date +%Y-%m-%d`
    COMP_DATE=`date -d"${RERAIN_DAYS} day ago ${DATA_NOW}" +%Y-%m-%d`
    DAY_DIFF=`differDay $DATA_NOW $1 `
    if [[ $DAY_DIFF -gt $RERAIN_DAYS ]]; then
        format_date=`echo $1| sed 's/-/\./g'`
        echo "$1时间早于$COMP_DATE, 与当前日期相差${DAY_DIFF}天属于${RERAIN_DAYS}天前的数据, 执行删除命令 => curl -XDELETE http://${ES_HOST}/${INDEX_START_WITH}*$format_date =>"`curl ${AUTH_INFO} -s -XDELETE http://${ES_HOST}/${INDEX_START_WITH}*$format_date`
    fi
}

# 找到所有index进行遍历，提取日期进行遍历，将2020.01.01的日期格式转为2020-01-01的格式
curl ${AUTH_INFO} -s -XGET http://${ES_HOST}/_cat/indices | grep "${INDEX_START_WITH}" | awk -F" " '{print $3}' | awk -F"-" '{print $NF}' | egrep "[0-9]*\.[0-9]*\.[0-9]*" | sort | uniq  | sed 's/\./-/g' | while read LINE
do
    if [ ! -n "$LINE" ] ;then
        continue;
    fi
    delete_indices $LINE
done
