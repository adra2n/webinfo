import os
import json
import socket
from IPy import IP
from config import config
from core.context import ScanContext
from utils.output import log


def _resolve_domain(domain: str) -> list[str]:
    """DNS 解析获取 IP"""
    ips = []
    try:
        for info in socket.getaddrinfo(domain, None):
            ip = info[4][0]
            if ip not in ips:
                ips.append(ip)
    except Exception:
        pass
    return ips


def _get_cidr(ip_str: str) -> str:
    """获取 IP 所在的 /24 网段"""
    try:
        ip = IP(ip_str)
        # 取前三个字节作为 /24 网段
        parts = ip_str.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        return ""


def scan(context: ScanContext):
    """从子域名结果提取资产（IP/hosts），并发现 CIDR 网段"""
    log.info(f"开始资产提取: {context.domain}")

    # 获取所有子域名
    subs = context.db.query(
        "SELECT name FROM subdomain WHERE scan_id=?", (context.scan_id,)
    )

    if not subs:
        log.warning("无子域名数据，请先执行 -dm")
        return

    ip_set = set()
    host_set = set()
    cidr_set = set()

    for row in subs:
        name = row["name"]
        host_set.add(name)

        # DNS 解析获取 IP
        ips = _resolve_domain(name)
        for ip in ips:
            ip_set.add(ip)

            # 更新子域名记录的 IP
            context.db.conn.execute(
                "UPDATE subdomain SET ip=? WHERE scan_id=? AND name=?",
                (ip, context.scan_id, name),
            )

            # 获取 CIDR 网段
            cidr = _get_cidr(ip)
            if cidr and cidr not in cidr_set:
                cidr_set.add(cidr)
                context.db.add_asset(context.scan_id, "cidr", cidr)

    context.db.conn.commit()

    # 写入 hosts 文件（用于后续端口扫描）
    with open(context.hosts_file, "w") as f:
        for h in sorted(host_set):
            f.write(h + "\n")

    # 写入 IP 文件
    with open(context.ips_file, "w") as f:
        for ip in sorted(ip_set):
            f.write(ip + "\n")

    # 写入 CIDR 文件（用于后续 C 段扫描）
    cidr_file = os.path.join(context.cache_dir, "cidr.txt")
    with open(cidr_file, "w") as f:
        for cidr in sorted(cidr_set):
            f.write(cidr + "\n")

    # 写入数据库
    for ip in sorted(ip_set):
        context.db.add_asset(context.scan_id, "ip", ip)
    for host in sorted(host_set):
        context.db.add_asset(context.scan_id, "host", host)

    context.mark_step_done("host")
    log.info(f"资产提取完成: {len(ip_set)} IPs, {len(host_set)} hosts, {len(cidr_set)} CIDRs")
