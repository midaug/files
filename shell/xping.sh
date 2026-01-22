#!/bin/bash

# 设置目标主机、Ping次数和间隔时间
TARGET_HOST="${1:-223.5.5.5}"  # 默认值
PING_COUNT="${2:-20}"          # 默认Ping 20次
PING_INTERVAL="${3:-0.3}"      # 默认间隔 0.3 秒

# 注意：只有超级用户才能设置小于0.2秒的间隔
if [ "$(id -u)" -ne 0 ] && [ $(echo "$PING_INTERVAL < 0.2" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
    echo "警告：间隔时间设置小于0.2秒通常需要root权限。"
    echo "部分系统可能无法生效，或者请尝试使用sudo运行脚本。"
fi

echo "开始Ping测试..."
echo "目标主机: $TARGET_HOST"
echo "Ping次数: $PING_COUNT"
echo "包间隔: $PING_INTERVAL 秒"
echo "================================"

echo "正在Ping，请稍候..."
echo "--------------------------------"

# 使用数组存储时间数据
PING_TIMES=()

# 执行ping命令，逐行处理输出
{
    # 运行ping命令，逐行读取输出
    while IFS= read -r line; do
        # 实时显示每一行输出
        echo "$line"
        
        # 检查是否包含时间信息
        if [[ "$line" == *time=* ]]; then
            # 提取时间值
            time_val=$(echo "$line" | grep -o 'time=[0-9.]*' | cut -d= -f2)
            if [[ -n "$time_val" ]]; then
                PING_TIMES+=("$time_val")
            fi
        fi
    done < <(ping -c "$PING_COUNT" -i "$PING_INTERVAL" "$TARGET_HOST" 2>&1)
}

echo "--------------------------------"

DATA_COUNT=${#PING_TIMES[@]}

# 检查是否成功收集到数据
if [ "$DATA_COUNT" -eq 0 ]; then
    echo "错误: 无法从目标主机获取数据。"
    echo "可能的原因："
    echo "1. 主机不响应Ping请求"
    echo "2. 网络连接故障"
    echo "3. 防火墙阻止了ICMP数据包"
    exit 1
fi

echo "数据收集完成，有效响应: $DATA_COUNT/$PING_COUNT"

# 计算丢包率
LOST_COUNT=$((PING_COUNT - DATA_COUNT))
LOSS_RATE=$(echo "scale=2; $LOST_COUNT * 100 / $PING_COUNT" | bc 2>/dev/null || echo 0)

echo "====== Ping统计结果 ======"
printf "丢包率: %d/%d (%.2f%%)\n" $LOST_COUNT $PING_COUNT $LOSS_RATE

# 如果有数据，进行详细统计
if [ "$DATA_COUNT" -gt 0 ]; then
    # 将数组元素传递给awk
    printf '%s\n' "${PING_TIMES[@]}" | awk -v count="$DATA_COUNT" -v lost_count="$LOST_COUNT" -v total_count="$PING_COUNT" '
    BEGIN {
        sum = 0
        min = 999999
        max = 0
    }
    {
        data[NR] = $1
        sum += $1
        if ($1 < min) min = $1
        if ($1 > max) max = $1
    }
    END {
        if (count == 0) {
            print "无有效数据"
            exit
        }
        
        avg = sum / count
        
        # 对数据进行排序(简单冒泡排序)
        for (i = 1; i <= count; i++) {
            for (j = i + 1; j <= count; j++) {
                if (data[j] < data[i]) {
                    temp = data[i]
                    data[i] = data[j]
                    data[j] = temp
                }
            }
        }
        
        printf "最小值: %.2f ms\n", min
        printf "最大值: %.2f ms\n", max
        printf "平均值: %.2f ms\n", avg
        print "------------------------"
        print "延迟百分位数(ms):"
        
        # 计算指定的百分位数
        n = split("50 60 70 80 85 90 95 99", percentiles)
        for (i = 1; i <= n; i++) {
            p = percentiles[i]
            pos = p / 100 * (count - 1) + 1
            idx = int(pos)
            frac = pos - idx
            
            if (idx >= count) {
                value = data[count]
            } else if (idx <= 1) {
                value = data[1]
            } else {
                value = data[idx] + frac * (data[idx + 1] - data[idx])
            }
            
            printf "P%-2d (%2d%%): %8.2f ms\n", p, p, value
        }
        
        # 显示数据分布概览
        print "------------------------"
        print "数据分布概览(ms):"
        if (count >= 5) {
            printf "最低5个值: "
            for (i = 1; i <= 5 && i <= count; i++) printf "%.1f ", data[i]
            printf "\n"
            
            if (count > 5) {
                printf "最高5个值: "
                for (i = (count-4 > 1 ? count-4 : 1); i <= count; i++) printf "%.1f ", data[i]
                printf "\n"
            }
        }
    }'
fi
