#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 这是一个python版本的ping工具，支持更详细的ping延迟分析

import sys
import subprocess
import platform
import time
import re
import math
import os
import argparse
import socket

def resolve_domain(domain):
    """
    解析域名获取实际IP地址
    """
    try:
        # 使用socket解析域名
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None

def ping_host(host, count=4, interval=1000, verbose=True):
    """
    Ping指定的主机并返回结果统计（跨平台兼容版本）
    """
    system = platform.system().lower()
    
    # 解析域名获取实际IP
    resolved_ip = None
    if not is_ip_address(host):
        resolved_ip = resolve_domain(host)
        if resolved_ip:
            if verbose:
                print("域名 {} 解析为 IP: {}".format(host, resolved_ip))
        else:
            if verbose:
                print("警告: 无法解析域名 {}, 将直接使用域名进行ping测试".format(host))
    
    if verbose:
        target_display = "{} ({})".format(host, resolved_ip) if resolved_ip else host
        print("开始ping {}，发送 {} 个数据包，间隔 {} 毫秒...".format(target_display, count, interval))
        print("-" * 70)
    
    if system == "windows":
        return ping_windows(host, count, interval, verbose, resolved_ip)
    else:
        return ping_unix(host, count, interval, verbose, system, resolved_ip)

def is_ip_address(host):
    """
    检查输入的是否是IP地址
    """
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if ip_pattern.match(host):
        return True
    return False

def ping_windows(host, count, interval, verbose, resolved_ip):
    """
    Windows专用的ping实现
    """
    times = []
    received = 0
    
    # 使用解析后的IP进行ping（如果解析成功）
    ping_target = resolved_ip if resolved_ip else host
    
    for i in range(count):
        try:
            ping_cmd = ["ping", "-n", "1", "-w", "1000", ping_target]
            
            env = os.environ.copy()
            env["LANG"] = "C"
            env["LC_ALL"] = "C"
            
            process = subprocess.Popen(ping_cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, env=env)
            output, error = process.communicate()
            
            if sys.version_info[0] >= 3:
                output_str = output.decode('utf-8', errors='ignore')
            else:
                output_str = output
            
            time_val = parse_windows_ping_output(output_str)
            
            if time_val is not None:
                times.append(time_val)
                received += 1
                if verbose:
                    # 显示域名和实际IP
                    if resolved_ip and not is_ip_address(host):
                        print("[{}/{}] 来自 {} ({}) 的回复: 字节=32 时间={:.1f}ms TTL=估算".format(
                            i+1, count, host, resolved_ip, time_val))
                    else:
                        print("[{}/{}] 来自 {} 的回复: 字节=32 时间={:.1f}ms TTL=估算".format(
                            i+1, count, ping_target, time_val))
            else:
                if verbose:
                    if resolved_ip and not is_ip_address(host):
                        print("[{}/{}] 请求超时 ({} -> {})".format(i+1, count, host, resolved_ip))
                    else:
                        print("[{}/{}] 请求超时。".format(i+1, count))
            
            if i < count - 1:
                time.sleep(interval / 1000.0)
                
        except Exception as e:
            if verbose:
                if resolved_ip and not is_ip_address(host):
                    print("[{}/{}] Ping失败: {} ({} -> {})".format(i+1, count, str(e), host, resolved_ip))
                else:
                    print("[{}/{}] Ping失败: {}".format(i+1, count, str(e)))
            continue
    
    return {
        "host": host,
        "resolved_ip": resolved_ip,
        "transmitted": count,
        "received": received,
        "times": times,
        "system": "windows"
    }

def ping_unix(host, count, interval, verbose, system, resolved_ip):
    """
    Unix-like系统（Linux/macOS）的ping实现
    """
    times = []
    received = 0
    
    # 使用解析后的IP进行ping（如果解析成功）
    ping_target = resolved_ip if resolved_ip else host
    
    for i in range(count):
        try:
            if system == "darwin":
                ping_cmd = ["ping", "-c", "1", "-t", "1", ping_target]
            else:
                ping_cmd = ["ping", "-c", "1", "-W", "1", ping_target]
            
            env = os.environ.copy()
            env["LANG"] = "C"
            env["LC_ALL"] = "C"
            
            process = subprocess.Popen(ping_cmd, stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, env=env)
            output, error = process.communicate()
            
            if sys.version_info[0] >= 3:
                output_str = output.decode('utf-8', errors='ignore')
            else:
                output_str = output
            
            time_val = parse_unix_ping_output(output_str, system)
            
            if time_val is not None:
                times.append(time_val)
                received += 1
                if verbose:
                    if system == "darwin":
                        if resolved_ip and not is_ip_address(host):
                            print("[{}/{}] 64 bytes from {} ({}): icmp_seq={} ttl=估算 time={:.1f} ms".format(
                                i+1, count, host, resolved_ip, i+1, time_val))
                        else:
                            print("[{}/{}] 64 bytes from {}: icmp_seq={} ttl=估算 time={:.1f} ms".format(
                                i+1, count, ping_target, i+1, time_val))
                    else:
                        if resolved_ip and not is_ip_address(host):
                            print("[{}/{}] 64 bytes from {} ({}): icmp_seq={} ttl=64 time={:.1f} ms".format(
                                i+1, count, host, resolved_ip, i+1, time_val))
                        else:
                            print("[{}/{}] 64 bytes from {}: icmp_seq={} ttl=64 time={:.1f} ms".format(
                                i+1, count, ping_target, i+1, time_val))
            else:
                if verbose:
                    if resolved_ip and not is_ip_address(host):
                        print("[{}/{}] From {} ({}) icmp_seq={} Destination Host Unreachable".format(
                            i+1, count, host, resolved_ip, i+1))
                    else:
                        print("[{}/{}] From {} icmp_seq={} Destination Host Unreachable".format(
                            i+1, count, ping_target, i+1))
            
            if i < count - 1:
                time.sleep(interval / 1000.0)
                
        except Exception as e:
            if verbose:
                if resolved_ip and not is_ip_address(host):
                    print("[{}/{}] Ping失败: {} ({} -> {})".format(i+1, count, str(e), host, resolved_ip))
                else:
                    print("[{}/{}] Ping失败: {}".format(i+1, count, str(e)))
            continue
    
    return {
        "host": host,
        "resolved_ip": resolved_ip,
        "transmitted": count,
        "received": received,
        "times": times,
        "system": system
    }

def parse_windows_ping_output(output):
    """
    解析Windows ping命令的输出
    """
    patterns = [
        r'time[=<>](\d+)\s*ms',
        r'time[=<>](\d+)ms',
        r'时间[=<>](\d+)\s*ms'
    ]
    
    for line in output.split('\n'):
        line = line.strip().lower()
        if 'reply from' in line or '来自' in line:
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue
    return None

def parse_unix_ping_output(output, system):
    """
    解析Unix-like系统ping命令的输出
    """
    patterns = [
        r'time[=<>](\d+\.?\d*)\s*ms',
        r'time[=<>](\d+\.?\d*)ms'
    ]
    
    for line in output.split('\n'):
        line = line.strip()
        if 'time=' in line.lower() or 'ttl=' in line.lower():
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue
    return None

def calculate_statistics(result):
    """
    计算ping统计信息
    """
    if not result["times"]:
        return {
            "packet_loss": 100.0,
            "error": "No successful ping responses"
        }
    
    times = sorted(result["times"])
    transmitted = result["transmitted"]
    received = result["received"]
    
    packet_loss = ((transmitted - received) / float(transmitted)) * 100
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    percentiles = {
        "p99": calculate_percentile(times, 99),
        "p95": calculate_percentile(times, 95),
        "p90": calculate_percentile(times, 90),
        "p85": calculate_percentile(times, 85),
        "p80": calculate_percentile(times, 80),
        "p70": calculate_percentile(times, 70),
        "p60": calculate_percentile(times, 60),
        "p50": calculate_percentile(times, 50),
    }
    
    return {
        "transmitted": transmitted,
        "received": received,
        "packet_loss": packet_loss,
        "average": avg_time,
        "minimum": min_time,
        "maximum": max_time,
        "percentiles": percentiles,
        "all_times": times
    }

def calculate_percentile(data, percentile):
    """
    计算百分位数
    """
    if not data:
        return 0
    
    k = (len(data) - 1) * (percentile / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    
    if f == c:
        return data[int(k)]
    
    d0 = data[int(f)] * (c - k)
    d1 = data[int(c)] * (k - f)
    return d0 + d1

def print_results(result, stats, host):
    """
    打印格式化的结果
    """
    system_name = "Windows" if result.get("system") == "windows" else \
                 "macOS" if result.get("system") == "darwin" else "Linux/Unix"
    
    # 显示域名和解析的IP
    target_display = host
    if result.get("resolved_ip") and not is_ip_address(host):
        target_display = "{} ({})".format(host, result.get("resolved_ip"))
    
    print("\n" + "="*70)
    print("PING 统计信息 - {} (运行在 {})".format(target_display, system_name))
    print("="*70)
    
    print("基本统计:")
    print("  数据包: 已发送 = {}, 已接收 = {}, 丢失 = {} ({:.1f}% 丢失)".format(
        stats["transmitted"], stats["received"], 
        stats["transmitted"] - stats["received"], stats["packet_loss"]))
    
    if stats["received"] > 0:
        print("  往返行程估计时间(以毫秒为单位):")
        print("    最短 = {:.2f}ms，最长 = {:.2f}ms，平均 = {:.2f}ms".format(
            stats["minimum"], stats["maximum"], stats["average"]))
        
        print("\n百分位数 (毫秒):")
        percentiles = stats["percentiles"]
        print("  P50 (中位数): {:.2f}ms".format(percentiles["p50"]))
        print("  P60: {:.2f}ms".format(percentiles["p60"]))
        print("  P70: {:.2f}ms".format(percentiles["p70"]))
        print("  P80: {:.2f}ms".format(percentiles["p80"]))
        print("  P85: {:.2f}ms".format(percentiles["p85"]))
        print("  P90: {:.2f}ms".format(percentiles["p90"]))
        print("  P95: {:.2f}ms".format(percentiles["p95"]))
        print("  P99: {:.2f}ms".format(percentiles["p99"]))
        
        if len(stats["all_times"]) <= 20:
            print("\n所有响应时间 (ms): {}".format(
                ", ".join("{:.2f}".format(t) for t in stats["all_times"])))
    else:
        print("  目标主机不可达")
    
    if "error" in result:
        print("\n错误: {}".format(result["error"]))
    
    print("="*70)

def parse_arguments():
    """
    使用argparse解析命令行参数
    """
    parser = argparse.ArgumentParser(
        description="Python Ping工具 - 跨平台兼容的ping测试脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ping_tool.py 8.8.8.8
  python ping_tool.py google.com -c 10 -i 500
  python ping_tool.py 192.168.1.1 --count 5 --interval 2000
        
兼容Python 2.7和3.x，支持Windows、macOS和Linux系统。
        """
    )
    
    parser.add_argument(
        'host',
        help='要ping的主机地址（IP或域名）'
    )
    
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=4,
        help='ping次数（默认: 4）',
        metavar='COUNT'
    )
    
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=1000,
        help='ping间隔时间，单位毫秒（默认: 1000）',
        metavar='MS'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='安静模式，不显示每个ping的详细结果'
    )
    
    return parser.parse_args()

def main():
    """
    主函数
    """
    try:
        args = parse_arguments()
        
        host = args.host
        count = max(1, min(args.count, 100))
        interval = max(200, min(args.interval, 10000))
        verbose = not args.quiet
        
        system = platform.system().lower()
        if system != "windows" and interval < 200 and verbose:
            print("警告: 在Linux/macOS上，间隔时间小于200ms可能需要root权限！")
        
        result = ping_host(host, count, interval, verbose)
        
        if "error" in result and not result["times"]:
            print("错误: {}".format(result["error"]))
            return
        
        stats = calculate_statistics(result)
        
        print_results(result, stats, host)
        
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
    except Exception as e:
        print("发生错误: {}".format(str(e)))
        print("\n使用 --help 参数查看使用方法")

if __name__ == "__main__":
    main()
