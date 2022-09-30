#!/bin/bash
# 备份hdfs上的数据，需要安装hdfs命令并联通hdfs集群
# 这里是将hdfs上的数据一天一天下载到本地目录backup_dir，backup_dir可以是挂载的nfs

# 本地存储位置
backup_dir=/mnt/nfs
# hdfs上数据的目录，一般为 /xx业务/20200101, 这里填的就是"xx业务"
hdfs_data_dir=xxxx
# 开始下载日期
first_day=${1:-20200101}
# 控制下载到离当前时间前几天为止，这里是3天，如果今天是20210930那么最多下载到20220927日，这是为了防止kafka中还有堆积的数据未写入HDFS
RERAIN_DAYS=3 

function differDay(){
    a=`date --date="$1" +%s`
    b=`date --date="$2" +%s`
    c=`expr $a - $b`
    d=`expr "scale=0;$c / 3600 / 24"|bc`
    echo $d
}

# 从传入的开始日期开始到当前日期为止
for i in `seq 99999`;do
    sync_date=`date +%Y%m%d -d "+$i days $first_day"`
    DATA_NOW=`date +%Y%m%d`
    COMP_DATE=`date -d"${RERAIN_DAYS} day ago ${DATA_NOW}" +%Y%m%d`
    sync_dir=$backup_dir/$hdfs_data_dir/$sync_date
    # 判断是否已经备份
    if [ -d "${sync_dir}" ]; then
        echo "${sync_dir} 已存在"
        continue
    fi 
    # 到当前日期为止
    if [ $sync_date -gt $DATA_NOW ]; then
        break
    fi
    # 略过暂不下载的时间
    if [ $sync_date -gt $COMP_DATE ]; then
	    continue
    fi
    DAY_DIFF=`differDay $DATA_NOW $sync_date `
    echo "----------------> sync_date=$sync_date DATA_NOW=$DATA_NOW COMP_DATE=$COMP_DATE DAY_DIFF=$DAY_DIFF"
    echo "开始从hdfs下载 $sync_date 的records文件"
    hdfs dfs -get /$hdfs_data_dir/$sync_date $backup_dir/$hdfs_data_dir/$sync_date
    echo "从hdfs下载records文件完成"
done
