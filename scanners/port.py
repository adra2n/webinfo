import os
import re
import json
import subprocess
import time
import threading
import queue
from config import config
from core.context import ScanContext
from utils.process import run_cmd
from utils.output import log

# 危险端口和服务映射
RISKY_SERVICES = {
    21: ("FTP", "高危", "支持匿名登录/弱口令"),
    23: ("Telnet", "高危", "明文传输，已废弃"),
    25: ("SMTP", "中危", "可能被用于邮件伪造"),
    110: ("POP3", "中危", "明文传输"),
    135: ("MSRPC", "高危", "Windows 远程过程调用"),
    139: ("NetBIOS", "高危", "SMB 漏洞"),
    445: ("SMB", "高危", "永恒之蓝等漏洞"),
    1433: ("MSSQL", "高危", "数据库暴露"),
    1434: ("MSSQL Browser", "高危", "数据库信息泄露"),
    3306: ("MySQL", "中危", "数据库暴露"),
    3389: ("RDP", "高危", "暴力破解/漏洞"),
    5432: ("PostgreSQL", "中危", "数据库暴露"),
    5900: ("VNC", "高危", "远程桌面，可能无密码"),
    6379: ("Redis", "高危", "默认无密码"),
    9200: ("Elasticsearch", "高危", "默认无认证"),
    11211: ("Memcached", "高危", "DDoS 放大"),
    27017: ("MongoDB", "高危", "默认无认证"),
    50000: ("SAP", "中危", "管理接口暴露"),
}

# 常见高危版本关键词
VULN_VERSIONS = [
    ("OpenSSH", ["7.4", "7.5", "7.6", "7.7"], "低版本，支持弱加密算法"),
    ("nginx", ["1.12", "1.14", "1.16"], "老版本，存在已知 CVE"),
    ("Apache", ["2.4.20", "2.4.25", "2.4.29"], "老版本，存在已知 CVE"),
    ("MySQL", ["5.5", "5.6", "5.7.30"], "老版本，存在已知 CVE"),
    ("MongoDB", ["3.0", "3.2", "3.6"], "老版本，存在已知 CVE"),
    ("Redis", ["3.0", "4.0", "5.0"], "老版本，存在已知 CVE"),
]


def _run_naabu_with_progress(context: ScanContext, targets_file: str, ports: str, rate: int, label: str) -> list[dict]:
    """naabu 扫描，带实时进度显示"""
    output_json = os.path.join(context.cache_dir, f"naabu_{label}.json")

    cmd = [
        os.path.expanduser("~/go/bin/naabu"),
        "-l", targets_file,
        "-p", ports,
        "-rate", str(rate),
        "-scan-type", config.NAABU_SCAN_TYPE,
        "-wn",
        "-ec",
        "-json",
        "-o", output_json,
    ]

    # 先统计目标数和读取目标列表
    with open(targets_file) as f:
        target_list = [line.strip() for line in f if line.strip()]
        target_count = len(target_list)

    log.info(f"[{label}] 目标数: {target_count}, 端口: {ports}, 速率: {rate}/s")

    # 启动 naabu，捕获 stderr 用于进度显示
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    start_time = time.time()
    found_count = 0
    hosts_with_ports = set()  # 记录已发现端口的主机
    scanned_hosts = set()  # 记录已扫描的主机
    current_target = target_list[0] if target_list else "无目标"
    last_found = ""  # 最近发现的端口
    
    def _format_time(seconds):
        """格式化时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _print_progress():
        """打印进度条"""
        elapsed = time.time() - start_time
        scanned_count = len(scanned_hosts)
        
        if scanned_count > 0 and elapsed > 0:
            rate_actual = scanned_count / elapsed
            remaining = target_count - scanned_count
            eta = remaining / rate_actual if rate_actual > 0 else 0
            
            # 计算进度条长度
            bar_length = 40
            progress = scanned_count / target_count if target_count > 0 else 0
            filled = int(bar_length * progress)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"\r[ETA {_format_time(eta)}] |{bar}| {scanned_count}/{target_count} rate: {rate_actual:.0f} qps (time: {_format_time(elapsed)}) found: {found_count} ports {last_found} | scanning: {current_target}    ", end="", flush=True)
        else:
            print(f"\r[{label}] 准备中... | scanning: {current_target}", end="", flush=True)

    # 显示初始进度
    _print_progress()

    # 使用线程和队列同时读取 stdout 和 stderr
    q = queue.Queue()
    
    def _reader(stream, label):
        for line in stream:
            q.put((label, line))
        q.put(('done', label))
    
    stdout_thread = threading.Thread(target=_reader, args=(proc.stdout, "stdout"))
    stderr_thread = threading.Thread(target=_reader, args=(proc.stderr, "stderr"))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    # 处理输出
    done_count = 0
    while done_count < 2:
        try:
            source, line = q.get(timeout=0.1)
        except queue.Empty:
            continue
        
        if source == "done":
            done_count += 1
            continue
        
        line = line.strip()
        
        if source == "stdout":
            # stdout: JSON 格式结果
            if line.startswith("{") and "host" in line and "port" in line:
                try:
                    data = json.loads(line)
                    host = data.get("host", "")
                    port = data.get("port", 0)
                    found_count += 1
                    last_found = f"[+] {host}:{port}"
                    if host not in scanned_hosts:
                        scanned_hosts.add(host)
                        for t in target_list:
                            if t not in scanned_hosts:
                                current_target = t
                                break
                        else:
                            current_target = "完成"
                    _print_progress()
                except json.JSONDecodeError:
                    pass
        elif source == "stderr":
            # stderr: 信息日志
            # 解析 naabu 的进度输出: "Found X ports on host xxx"
            if "Found" in line and "ports" in line and "on host" in line:
                found_match = re.search(r"Found\s+(\d+)\s+ports?\s+on\s+host\s+(\S+)", line)
                if found_match:
                    host = found_match.group(2)
                    if host not in scanned_hosts:
                        scanned_hosts.add(host)
                        for t in target_list:
                            if t not in scanned_hosts:
                                current_target = t
                                break
                        else:
                            current_target = "完成"
                    _print_progress()
            # 跳过 banner 和其他信息
            elif "projectdiscovery" in line or "naabu version" in line:
                pass
            elif "Running" in line or "Host discovery" in line:
                pass
            elif line.startswith("[INF]") or line.startswith("[WRN]"):
                pass

    stdout_thread.join()
    stderr_thread.join()
    print()  # 换行
    proc.wait()

    return _parse_output(output_json)


def _parse_output(filepath: str) -> list[dict]:
    """解析 naabu 输出"""
    results = []
    if not os.path.exists(filepath):
        return results
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                host = data.get("host", "")
                ip = data.get("ip", host)
                port = data.get("port", 0)

                # 提取 nmap 服务信息
                service = data.get("service", {})
                service_name = service.get("name", "") if isinstance(service, dict) else ""
                product = service.get("product", "") if isinstance(service, dict) else ""
                version = service.get("version", "") if isinstance(service, dict) else ""

                results.append({
                    "ip": ip,
                    "host": host,
                    "port": port,
                    "state": "open",
                    "service": service_name,
                    "product": f"{product} {version}".strip(),
                    "source": "naabu",
                })
            except json.JSONDecodeError:
                continue
    return results


def _check_security_issues(port: int, service: str, product: str) -> list[str]:
    """检查安全问题"""
    issues = []

    # 检查危险端口
    if port in RISKY_SERVICES:
        svc, risk, desc = RISKY_SERVICES[port]
        issues.append(f"[{risk}] {svc}: {desc}")

    # 检查高危版本
    for vuln_svc, vuln_versions, desc in VULN_VERSIONS:
        if vuln_svc.lower() in product.lower():
            for v in vuln_versions:
                if v in product:
                    issues.append(f"[中危] {vuln_svc}: {desc}")
                    break

    # 检查无认证服务
    if port == 6379 and "redis" in service.lower():
        issues.append("[高危] Redis: 可能无密码认证")
    if port == 27017 and "mongodb" in service.lower():
        issues.append("[高危] MongoDB: 可能无认证")
    if port == 9200 and "elasticsearch" in service.lower():
        issues.append("[高危] Elasticsearch: 可能无认证")

    return issues


def _print_results_summary(context: ScanContext, ports: list[dict]):
    """打印扫描结果汇总"""
    if not ports:
        log.info("未发现开放端口")
        return

    print("\n" + "=" * 80)
    print("扫描结果汇总")
    print("=" * 80)

    # 按 IP 分组
    ip_groups = {}
    for p in ports:
        ip = p["ip"]
        if ip not in ip_groups:
            ip_groups[ip] = []
        ip_groups[ip].append(p)

    total_issues = 0
    for ip in sorted(ip_groups.keys()):
        items = ip_groups[ip]
        print(f"\n{ip} ({len(items)} 个开放端口)")
        print("-" * 60)
        print(f"{'端口':<8} {'服务':<15} {'产品/版本':<25} {'安全问题'}")
        print("-" * 60)

        for p in sorted(items, key=lambda x: x["port"]):
            port = p["port"]
            service = p["service"] or "-"
            product = p["product"] or "-"
            issues = _check_security_issues(port, p["service"], p["product"])

            if issues:
                issue_str = issues[0]
                total_issues += len(issues)
            else:
                issue_str = "-"

            print(f"{port:<8} {service:<15} {product:<25} {issue_str}")

            # 输出额外的安全问题
            for issue in issues[1:]:
                print(f"{'':8} {'':15} {'':25} {issue}")

    print("\n" + "=" * 80)
    print(f"总计: {len(ports)} 个开放端口, {len(ip_groups)} 个 IP")
    if total_issues > 0:
        print(f"⚠ 发现 {total_issues} 个潜在安全问题")
    print("=" * 80)


def scan(context: ScanContext):
    """naabu + nmap 联合扫描，支持 CIDR 扩展"""
    log.info("开始端口扫描")

    # Step 1: 扫描原始目标（全端口）
    discovered = _run_naabu_with_progress(context, context.hosts_file, config.NAABU_PORTS, config.NAABU_RATE, "原始目标")
    log.info(f"原始目标发现 {len(discovered)} 个开放端口")

    # Step 2: CIDR 扩展扫描（top-1000）
    if config.EXPAND_CIDR:
        cidr_discovered = _run_naabu_with_progress(context, os.path.join(context.cache_dir, "cidr_list.txt"), config.CIDR_PORTS, config.CIDR_RATE, "CIDR扩展")
        log.info(f"CIDR 扩展发现 {len(cidr_discovered)} 个开放端口")
        discovered.extend(cidr_discovered)

    if discovered:
        # 去重（同一 IP + 端口）
        seen = set()
        unique = []
        for item in discovered:
            key = (item["ip"], item["port"])
            if key not in seen:
                seen.add(key)
                unique.append(item)
        discovered = unique

        # 写入数据库
        context.db.add_ports_batch(context.scan_id, discovered)

        # 打印结果汇总
        _print_results_summary(context, discovered)
    else:
        log.info("未发现开放端口")

    context.mark_step_done("sc")
    log.info("端口扫描完成")
