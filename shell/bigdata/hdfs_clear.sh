#!/bin/bash
# 根据备份清理hdfs上的数据，与hdfs_back.sh结合使用，建议手动执行
# 需要有hadoop命令，建议在hadoop集群中的master或header节点的hadoop用户下执行

# 本地备份目录 hdfs_back.sh 备份的位置
backup_dir=/mnt/nfs/xxx
# hdfs上数据的目录，一般为 /xx业务/20200101, 这里填的就是"xx业务"
hdfs_dir=/xxxx
# 保护时长，当前时间400天内的数据不会删除，一般保留近一年的数据用于分析
RERAIN_DAYS=400
# 保护日期，用于手动控制删到哪里结束
end_date_str=${1:-20210303}
end_date=`date +%Y%m%d -d "${end_date_str}"` #保护时间, hdfs上超过这个日期的数据不会被删除
# 获取hdfs上已存在的日期列表
hdfs_all_dir=`hadoop fs -ls ${hdfs_dir}/`

# 遍历备份目录
for r_date_dir in `ls $backup_dir`
do
    sync_date=`date +%Y%m%d -d "$r_date_dir"`
    DATA_NOW=`date +%Y%m%d`
    COMP_DATE=`date -d"${RERAIN_DAYS} day ago ${DATA_NOW}" +%Y%m%d`
    sync_dir=$backup_dir/$r_date_dir
   
    # 判断删除的日期是否大于传入的保护日期
    if [ $sync_date -gt $end_date ]; then
        echo "# !!! $hdfs_dir/$r_date_dir 在设定的保护日期end_date=${end_date}以后,暂时保留 !!!"
        continue    
    fi
    # 判断删除的日期是否大于设定的保护时长
    if [ $sync_date -gt $COMP_DATE ]; then
        echo "# !!! $hdfs_dir/$r_date_dir 在最近${RERAIN_DAYS}天内,暂时保留 !!!"
	    continue
    fi
    
    # 判断删除的日期是否在hdfs上存在
    if test -z "$(echo $hdfs_all_dir | grep "$hdfs_dir/$r_date_dir")"; then
        echo "# !!! $hdfs_dir/$r_date_dir 在hdfs上不存在 !!!"
        continue
    fi
    echo "---->已存在备份${sync_dir} ,开始清理 $hdfs_dir/$r_date_dir"
    hadoop fs -rm -skipTrash -r $hdfs_dir/$r_date_dir
done

