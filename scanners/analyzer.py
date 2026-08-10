import requests
from core.context import ScanContext
from utils.http import random_headers, build_url
from utils.output import log


def _analyze_headers(context: ScanContext):
    """响应头安全分析"""
    log.info("分析响应头安全性")

    ports = context.db.query(
        "SELECT host, port, service FROM port WHERE scan_id=? AND service='http'",
        (context.scan_id,),
    )

    for item in ports:
        host = item["host"]
        port = item["port"]
        url = build_url(host, port)

        try:
            resp = requests.get(url, headers=random_headers(), timeout=5, verify=False, allow_redirects=False)
            headers = resp.headers

            # 检查安全头缺失
            missing = []
            if "Content-Security-Policy" not in headers:
                missing.append("CSP")
            if "Strict-Transport-Security" not in headers:
                missing.append("HSTS")
            if "X-Content-Type-Options" not in headers:
                missing.append("X-Content-Type-Options")
            if "X-Frame-Options" not in headers:
                missing.append("X-Frame-Options")

            if len(missing) >= 3:
                context.db.add_finding(
                    context.scan_id,
                    category="header",
                    severity="Medium",
                    title=f"安全响应头缺失 ({', '.join(missing)})",
                    detail=f"{url} 缺少 {', '.join(missing)}",
                    evidence=str(dict(headers)),
                    host=host,
                    port=port,
                )

            # 检查信息泄露
            server = headers.get("Server", "")
            powered = headers.get("X-Powered-By", "")
            if server and any(v in server.lower() for v in ["apache/", "nginx/", "iis/", "tomcat/"]):
                context.db.add_finding(
                    context.scan_id,
                    category="header",
                    severity="Low",
                    title="Server 头版本泄露",
                    detail=f"{url} Server: {server}",
                    evidence=server,
                    host=host,
                    port=port,
                )
            if powered:
                context.db.add_finding(
                    context.scan_id,
                    category="header",
                    severity="Low",
                    title="X-Powered-By 信息泄露",
                    detail=f"{url} X-Powered-By: {powered}",
                    evidence=powered,
                    host=host,
                    port=port,
                )

        except Exception:
            continue


def _analyze_correlation(context: ScanContext):
    """资产关联分析"""
    log.info("分析资产关联")

    # 查找同一 IP 上多个域名
    rows = context.db.query(
        """SELECT ip, GROUP_CONCAT(DISTINCT name) as domains, COUNT(DISTINCT name) as cnt
           FROM subdomain WHERE scan_id=? AND ip != ''
           GROUP BY ip HAVING cnt > 1""",
        (context.scan_id,),
    )
    for row in rows:
        context.db.add_finding(
            context.scan_id,
            category="correlation",
            severity="Info",
            title=f"同一 IP 关联多个子域名",
            detail=f"IP {row['ip']} 关联: {row['domains']}",
            host=row["ip"],
        )

    # 查找非标准端口的 HTTP 服务
    rows = context.db.query(
        """SELECT host, port, service, title FROM port
           WHERE scan_id=? AND service='http' AND port NOT IN (80, 443, 8080, 8443)""",
        (context.scan_id,),
    )
    for row in rows:
        context.db.add_finding(
            context.scan_id,
            category="correlation",
            severity="Info",
            title=f"非标准端口 HTTP 服务",
            detail=f"{row['host']}:{row['port']} ({row['title']})",
            host=row["host"],
            port=row["port"],
        )


def scan(context: ScanContext):
    """深度分析"""
    log.info("开始深度分析")
    _analyze_headers(context)
    _analyze_correlation(context)
    log.info("深度分析完成")
