#!/bin/bash

SIZE=${1:-'64M'}
T_PATH=${2:-'/tmp/fio.test'}
echo "TEST SIZE:  ${SIZE}"
echo "TEST FILEPATH:  ${T_PATH}"

rm -f ${T_PATH}
echo -e "1--------读时延："
fio -direct=1 -iodepth=1 -rw=read -ioengine=libaio -bs=4k -size=${SIZE} -numjobs=1 -runtime=1000 -group_reporting -name=test -filename=${T_PATH}
echo -e "\n2--------写时延："
fio -direct=1 -iodepth=1 -rw=write -ioengine=libaio -bs=4k -size=${SIZE} -numjobs=1 -runtime=1000 -group_reporting -name=test -filename=${T_PATH}

rm -f ${T_PATH} 
echo -e "\n\n3--------读带宽："
fio -direct=1 -iodepth=32 -rw=read -ioengine=libaio -bs=256k -size=${SIZE} -numjobs=4 -runtime=1000 -group_reporting -name=test -filename=${T_PATH}
echo -e "\n4--------写带宽："
fio -direct=1 -iodepth=32 -rw=write -ioengine=libaio -bs=256k -size=${SIZE} -numjobs=4 -runtime=1000 -group_reporting -name=test -filename=${T_PATH}

rm -f ${T_PATH} 
echo -e "\n\n5--------读IOPS："
fio -direct=1 -iodepth=32 -rw=randread  -ioengine=libaio -bs=4k -size=${SIZE} -numjobs=4 -runtime=1000 -group_reporting -name=test -filename=${T_PATH}
echo -e "\n6--------写IOPS："
fio -direct=1 -iodepth=32 -rw=randwrite -ioengine=libaio -bs=4k -size=${SIZE} -numjobs=4 -runtime=1000 -group_reporting -name=test -filename=${T_PATH}

rm -f ${T_PATH}
