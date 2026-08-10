import os
import sys
import re
import readline
from config import config
from core.db import ScanDB
from core.context import ScanContext
from core.workflow import Workflow, Step, ALL_STEPS
from core.reporter import export_to_excel, export_summary
from utils.output import log
from utils.banner import showbanner


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


COMMANDS = {
    "scan":    "扫描域名",
    "show":    "查看结果",
    "list":    "列出所有扫描",
    "export":  "导出 Excel",
    "help":    "帮助",
    "quit":    "退出",
    "exit":    "退出",
}


def setup_completion():
    """设置命令补全"""
    completions = list(COMMANDS.keys())

    def completer(text, state):
        matches = [c for c in completions if c.startswith(text)]
        if state < len(matches):
            return matches[state]
        return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")


def parse_scan_command(text: str) -> dict | None:
    """解析扫描命令
    支持格式:
      scan example.com
      scan example.com --all
      scan example.com -dm -host
      scan example.com --force
      扫描 example.com
      全扫 example.com
      重扫 example.com
    """
    # 提取域名
    domain_match = re.search(r'([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)*\.[a-zA-Z]{2,})', text)
    if not domain_match:
        return None
    domain = domain_match.group(1)

    # 是否强制重跑
    force = bool(re.search(r'--force|强制|重扫|重跑', text))

    # 提取参数
    steps = []
    if re.search(r'--all|全扫|全部|完整', text):
        steps = ["dm", "host", "sc", "hack"]
    else:
        if re.search(r'-dm|子域名|域名枚举', text):
            steps.append("dm")
        if re.search(r'-host|资产|ip|提取', text):
            steps.append("host")
        if re.search(r'-sc|端口|port', text):
            steps.append("sc")
        if re.search(r'-dr|路径|path|目录', text):
            steps.append("dr")
        if re.search(r'-hack|漏洞|poc|扫描漏洞', text):
            steps.append("hack")

    # 如果没指定步骤，默认全扫
    if not steps:
        steps = ["dm", "host", "sc", "hack"]

    return {"domain": domain, "steps": steps, "force": force}


def parse_show_command(text: str) -> dict | None:
    """解析查看命令
    支持格式:
      show example.com              摘要
      show example.com -dm          子域名
      show example.com -host        资产/IP
      show example.com -sc          端口
      show example.com -dr          路径
      show example.com -hack        漏洞
      查看 example.com
      结果 example.com
    """
    domain_match = re.search(r'([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)*\.[a-zA-Z]{2,})', text)
    domain = domain_match.group(1) if domain_match else None

    # 提取查看类型
    view = "summary"
    if re.search(r'-dm|子域名', text):
        view = "subdomain"
    elif re.search(r'-host|资产|ip', text):
        view = "asset"
    elif re.search(r'-sc|端口|port', text):
        view = "port"
    elif re.search(r'-dr|路径|path|目录', text):
        view = "path"
    elif re.search(r'-hack|漏洞|poc|vuln', text):
        view = "vuln"

    return {"domain": domain, "view": view}


def parse_export_command(text: str) -> dict | None:
    """解析导出命令
    支持格式:
      export example.com
      导出 example.com
    """
    domain_match = re.search(r'([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)*\.[a-zA-Z]{2,})', text)
    if domain_match:
        return {"domain": domain_match.group(1)}
    return None


def run_scan(domain: str, steps: list[str], force: bool = False):
    """执行扫描"""
    step_names = {"dm": "子域名", "host": "资产", "sc": "端口", "dr": "路径", "hack": "漏洞"}
    print(f"\n{'='*50}")
    print(f"  开始扫描: {domain}")
    print(f"  步骤: {' → '.join(step_names.get(s, s) for s in steps)}")
    if force:
        print(f"  模式: 强制重跑")
    print(f"{'='*50}\n")

    with ScanDB() as db:
        ctx = ScanContext(domain, db)

        # 强制模式：清除已完成状态
        if force:
            ctx._state["steps_done"] = []
            ctx._save_state()

        step_enums = []
        for s in steps:
            if s == "dm":
                step_enums.append(Step.DOMAIN)
            elif s == "host":
                step_enums.append(Step.ASSET)
            elif s == "sc":
                step_enums.append(Step.PORT)
            elif s == "dr":
                step_enums.append(Step.PATH)
            elif s == "hack":
                step_enums.append(Step.VULN)

        wf = Workflow(ctx)
        wf.run(step_enums)

        print(f"\n{'='*50}")
        print(export_summary(db.db_path, domain))
        print(f"{'='*50}\n")


def show_results(domain: str, view: str = "summary"):
    """显示扫描结果"""
    with ScanDB() as db:
        scan = db.get_scan(domain)
        if not scan:
            print(f"\n  未找到 {domain} 的扫描记录\n")
            return

        scan_id = scan["id"]

        if view == "summary":
            print(f"\n{'='*60}")
            print(export_summary(db.db_path, domain))

            # 漏洞
            vulns = db.query(
                "SELECT host, port, level, vuln FROM vuln WHERE scan_id=? ORDER BY level",
                (scan_id,),
            )
            if vulns:
                print("\n  漏洞详情:")
                print(f"  {'-'*56}")
                for v in vulns:
                    print(f"  [{v['level']:8s}] {v['host']}:{v['port']} - {v['vuln']}")

            # 端口安全问题
            ports = db.query(
                "SELECT host, port, service, product, version FROM port WHERE scan_id=? ORDER BY host, port",
                (scan_id,),
            )
            security_issues = []
            for p in ports:
                port_num = p["port"]
                service = p["service"] or ""
                product = p["product"] or ""
                version = p["version"] or ""
                full_product = f"{product} {version}".strip()

                # 检查危险端口
                if port_num in RISKY_SERVICES:
                    svc, risk, desc = RISKY_SERVICES[port_num]
                    security_issues.append({
                        "host": p["host"],
                        "port": port_num,
                        "risk": risk,
                        "service": svc,
                        "detail": desc,
                    })

                # 检查高危版本
                for vuln_svc, vuln_versions, desc in VULN_VERSIONS:
                    if vuln_svc.lower() in full_product.lower():
                        for v in vuln_versions:
                            if v in full_product:
                                security_issues.append({
                                    "host": p["host"],
                                    "port": port_num,
                                    "risk": "中危",
                                    "service": vuln_svc,
                                    "detail": desc,
                                })
                                break

            if security_issues:
                print(f"\n  安全问题 ({len(security_issues)} 个):")
                print(f"  {'-'*56}")
                for issue in security_issues:
                    print(f"  [{issue['risk']}] {issue['host']}:{issue['port']} - {issue['service']}: {issue['detail']}")

            # 端口 Top 10
            port_stats = db.query(
                "SELECT service, COUNT(*) as cnt FROM port WHERE scan_id=? AND service != '' GROUP BY service ORDER BY cnt DESC LIMIT 10",
                (scan_id,),
            )
            if port_stats:
                print("\n  端口服务 Top 10:")
                print(f"  {'-'*56}")
                for p in port_stats:
                    bar = "█" * min(p["cnt"], 30)
                    print(f"  {p['service']:20s} {bar} {p['cnt']}")

            print(f"{'='*60}\n")

        elif view == "subdomain":
            rows = db.query(
                "SELECT name, ip, source FROM subdomain WHERE scan_id=? ORDER BY name",
                (scan_id,),
            )
            print(f"\n{'='*50}")
            print(f"  子域名 ({len(rows)} 条)")
            print(f"  {'-'*46}")
            for r in rows:
                ip = r["ip"] or "-"
                print(f"  {r['name']:<40s} {ip:<15s} {r['source'] or ''}")
            print(f"{'='*50}\n")

        elif view == "asset":
            rows = db.query(
                "SELECT type, value FROM asset WHERE scan_id=? ORDER BY type, value",
                (scan_id,),
            )
            ips = [r for r in rows if r["type"] == "ip"]
            hosts = [r for r in rows if r["type"] == "host"]
            cidrs = [r for r in rows if r["type"] == "cidr"]

            print(f"\n{'='*60}")
            print(f"  资产: {len(ips)} IPs, {len(hosts)} Hosts, {len(cidrs)} CIDRs")
            if ips:
                print(f"\n  IPs ({len(ips)}):")
                print(f"  {'-'*56}")
                for r in ips:
                    print(f"  {r['value']}")
            if hosts:
                print(f"\n  Hosts ({len(hosts)}):")
                print(f"  {'-'*56}")
                for r in hosts[:30]:
                    print(f"  {r['value']}")
                if len(hosts) > 30:
                    print(f"  ... 省略 {len(hosts)-30} 条")
            if cidrs:
                print(f"\n  CIDRs ({len(cidrs)}):")
                print(f"  {'-'*56}")
                for r in cidrs:
                    print(f"  {r['value']}")
            print(f"{'='*60}\n")

        elif view == "port":
            rows = db.query(
                "SELECT host, port, protocol, state, service, product, version FROM port WHERE scan_id=? ORDER BY host, port",
                (scan_id,),
            )
            print(f"\n{'='*80}")
            print(f"  端口扫描结果 ({len(rows)} 条)")
            print(f"  {'-'*76}")

            # 按主机分组
            host_groups = {}
            for r in rows:
                host = r["host"]
                if host not in host_groups:
                    host_groups[host] = []
                host_groups[host].append(r)

            total_issues = 0
            for host in sorted(host_groups.keys()):
                items = host_groups[host]
                print(f"\n  {host} ({len(items)} 个开放端口)")
                print(f"  {'-'*70}")
                print(f"  {'端口':<8} {'协议':<6} {'服务':<12} {'产品/版本':<25} {'安全问题'}")
                print(f"  {'-'*70}")

                for r in items:
                    port = r["port"]
                    protocol = r["protocol"] or "tcp"
                    service = r["service"] or "-"
                    prod = r["product"] or ""
                    ver = r["version"] or ""
                    product = f"{prod} {ver}".strip() or "-"

                    # 检查安全问题
                    issues = []
                    if port in RISKY_SERVICES:
                        svc, risk, desc = RISKY_SERVICES[port]
                        issues.append(f"[{risk}] {svc}: {desc}")

                    for vuln_svc, vuln_versions, desc in VULN_VERSIONS:
                        if vuln_svc.lower() in product.lower():
                            for v in vuln_versions:
                                if v in product:
                                    issues.append(f"[中危] {vuln_svc}: {desc}")
                                    break

                    if issues:
                        issue_str = issues[0]
                        total_issues += len(issues)
                    else:
                        issue_str = "-"

                    print(f"  {port:<8} {protocol:<6} {service:<12} {product:<25} {issue_str}")

                    for issue in issues[1:]:
                        print(f"  {'':8} {'':6} {'':12} {'':25} {issue}")

            print(f"\n{'='*80}")
            print(f"  总计: {len(rows)} 个端口, {len(host_groups)} 个主机")
            if total_issues > 0:
                print(f"  发现 {total_issues} 个潜在安全问题")
            print(f"{'='*80}\n")

        elif view == "path":
            rows = db.query(
                "SELECT host, path, status, length, redirect FROM path WHERE scan_id=? ORDER BY host, path",
                (scan_id,),
            )
            print(f"\n{'='*50}")
            print(f"  路径 ({len(rows)} 条)")
            print(f"  {'-'*46}")
            for r in rows:
                redir = r["redirect"] or ""
                print(f"  {r['host']:<30s} {r['status']:<6s} {r['path']:<40s} {r['length']:<8s} {redir}")
            print(f"{'='*50}\n")

        elif view == "vuln":
            rows = db.query(
                "SELECT host, port, level, vuln, detail FROM vuln WHERE scan_id=? ORDER BY level, host",
                (scan_id,),
            )
            print(f"\n{'='*50}")
            print(f"  漏洞 ({len(rows)} 条)")
            print(f"  {'-'*46}")
            for r in rows:
                print(f"  [{r['level']:<8s}] {r['host']}:{r['port']} - {r['vuln']}")
                if r["detail"]:
                    print(f"             {r['detail'][:80]}")
            print(f"{'='*50}\n")


def list_scans():
    """列出所有扫描"""
    with ScanDB() as db:
        scans = db.query("SELECT * FROM scan ORDER BY updated DESC")
        if not scans:
            print("\n  暂无扫描记录\n")
            return

        print(f"\n{'='*60}")
        print(f"  {'域名':<25s} {'状态':<15s} {'更新时间'}")
        print(f"  {'-'*56}")
        for s in scans:
            print(f"  {s['domain']:<25s} {s['status']:<15s} {s['updated']}")
        print(f"{'='*60}\n")


def export_xlsx(domain: str):
    """导出 Excel"""
    with ScanDB() as db:
        output = os.path.join(config.RESULT_DIR, f"{domain}.xlsx")
        export_to_excel(db.db_path, output)
        print(f"\n  已导出: {output}\n")


def show_help():
    """显示帮助"""
    print(f"""
{'='*50}
  webinfo 对话式命令帮助
{'='*50}

  扫描命令:
    scan example.com              全量扫描
    scan example.com --all        全量扫描（同上）
    scan example.com -dm -sc      仅子域名+端口
    scan example.com --force      强制重跑（忽略已完成步骤）
    扫描 example.com              中文也行
    重扫 example.com              强制重跑

  查看结果:
    show example.com              摘要（默认）
    show example.com -dm          子域名
    show example.com -host        资产/IP
    show example.com -sc          端口
    show example.com -dr          路径
    show example.com -hack        漏洞
    查看 example.com
    结果 example.com

  列出任务:
    list                          列出所有扫描

  导出:
    export example.com            导出 Excel

  其他:
    help                          帮助
    quit / exit                   退出

  快捷步骤:
    -dm   子域名枚举
    -host 资产提取
    -sc   端口扫描（分层）
    -dr   路径扫描
    -hack 漏洞扫描
{'='*50}
""")


def main():
    showbanner()
    setup_completion()

    print("  输入 help 查看帮助，quit 退出\n")

    while True:
        try:
            user_input = input("\033[95mwebinfo>\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见!")
            break

        if not user_input:
            continue

        # 解析命令
        lower = user_input.lower()

        if lower in ("quit", "exit", "q"):
            print("\n  再见!")
            break

        elif lower in ("help", "h", "?"):
            show_help()

        elif lower in ("list", "ls"):
            list_scans()

        elif lower.startswith(("scan", "扫描", "全扫")):
            params = parse_scan_command(user_input)
            if not params:
                print("\n  请指定域名，例如: scan example.com\n")
                continue
            run_scan(params["domain"], params["steps"], params.get("force", False))

        elif lower.startswith(("show", "查看", "结果")):
            params = parse_show_command(user_input)
            if not params or not params["domain"]:
                list_scans()
                continue
            show_results(params["domain"], params["view"])

        elif lower.startswith(("export", "导出")):
            params = parse_export_command(user_input)
            if not params:
                print("\n  请指定域名，例如: export example.com\n")
                continue
            export_xlsx(params["domain"])

        else:
            # 尝试当作 scan 命令
            params = parse_scan_command(user_input)
            if params:
                run_scan(params["domain"], params["steps"])
            else:
                print(f"\n  未知命令: {user_input}")
                print(f"  输入 help 查看帮助\n")


if __name__ == "__main__":
    main()
