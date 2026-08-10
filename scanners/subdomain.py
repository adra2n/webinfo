import os
import json
import subprocess
from config import config
from core.context import ScanContext
from utils.output import log


def scan(context: ScanContext):
    """pureDNS 子域名爆破"""
    log.info(f"开始子域名枚举: {context.domain}")

    wordlist = os.path.join(config.BASE_DIR, "db", "subdomains.txt")
    brute_out = os.path.join(context.cache_dir, "puredns_brute.txt")
    resolve_out = os.path.join(context.cache_dir, "puredns_resolved.txt")

    # Step 1: pureDNS 爆破
    cmd = [config.PUREDNS_BIN, "bruteforce", wordlist, context.domain]
    if os.path.exists(config.PUREDNS_RESOLVERS):
        cmd.extend(["--resolvers", config.PUREDNS_RESOLVERS])
    cmd.extend(["--rate-limit", str(config.PUREDNS_RATE)])
    cmd.extend(["--write", brute_out])

    log.info(f"执行: puredns bruteforce ... {context.domain}")
    subprocess.run(cmd, timeout=1800, stdin=subprocess.DEVNULL)

    if not os.path.exists(brute_out):
        log.error("pureDNS 爆破未生成结果")
        context.mark_step_done("dm")
        return

    # Step 2: 解析并过滤通配符
    cmd2 = [config.PUREDNS_BIN, "resolve", brute_out]
    if os.path.exists(config.PUREDNS_RESOLVERS):
        cmd2.extend(["--resolvers", config.PUREDNS_RESOLVERS])
    cmd2.extend(["--write", resolve_out])

    log.info("pureDNS 解析 + 通配符过滤")
    subprocess.run(cmd2, timeout=1800, stdin=subprocess.DEVNULL)

    # 读取结果写入数据库
    result_file = resolve_out if os.path.exists(resolve_out) else brute_out
    count = 0

    with open(result_file) as f:
        for line in f:
            subdomain = line.strip()
            if not subdomain or subdomain.startswith("#"):
                continue

            parts = subdomain.split(".")
            if len(parts) < 2:
                continue

            name = subdomain
            base_domain = ".".join(parts[-2:])

            context.db.add_subdomain(
                context.scan_id,
                name=name,
                domain=base_domain,
                ip="",
                cidr="",
                asn="",
                desc="",
                tag="",
                source="puredns",
            )
            count += 1

    context.mark_step_done("dm")
    log.info(f"子域名枚举完成，发现 {count} 条记录")
