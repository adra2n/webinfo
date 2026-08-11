import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    BASE_DIR = BASE_DIR

    # 工具路径（可环境变量覆盖）
    PUREDNS_BIN = os.getenv("WEBINFO_PUREDNS_BIN", os.path.expanduser("~/go/bin/puredns"))
    PUREDNS_RESOLVERS = os.getenv("WEBINFO_PUREDNS_RESOLVERS", os.path.expanduser("~/.config/puredns/resolvers.txt"))
    PUREDNS_RATE = int(os.getenv("WEBINFO_PUREDNS_RATE", "100"))  # 低速防封
    DIRSEARCH = os.getenv(
        "WEBINFO_DIRSEARCH",
        os.path.join(BASE_DIR, "bin", "dirsearch", "dirsearch.py"),
    )

    # 扫描参数
    THREADS = int(os.getenv("WEBINFO_THREADS", "50"))
    TIMEOUT = int(os.getenv("WEBINFO_TIMEOUT", "10"))
    IP_RANGE = int(os.getenv("WEBINFO_IP_RANGE", "5"))

    # 分层端口扫描 - 原始目标
    NAABU_RATE = int(os.getenv("WEBINFO_NAABU_RATE", "300"))
    NAABU_PORTS = os.getenv("WEBINFO_NAABU_PORTS", "1-65535")  # 全端口
    NAABU_SCAN_TYPE = os.getenv("WEBINFO_NAABU_SCAN_TYPE", "s")  # SYN 扫描
    NAABU_HOST_DISCOVERY = os.getenv("WEBINFO_NAABU_HOST_DISCOVERY", "true")  # 主机存活检测
    NAABU_EXCLUDE_CDN = os.getenv("WEBINFO_NAABU_EXCLUDE_CDN", "true")  # 排除 CDN
    NAABU_STREAM = os.getenv("WEBINFO_NAABU_STREAM", "true").lower() == "true"  # 流模式加速
    NAABU_THREADS = int(os.getenv("WEBINFO_NAABU_THREADS", "30"))  # 并发线程数
    NMAP_EXTRA_ARGS = os.getenv("WEBINFO_NMAP_EXTRA", "-sV -T4 --open --script=banner").split()

    # CIDR 扩展扫描
    EXPAND_CIDR = os.getenv("WEBINFO_EXPAND_CIDR", "true").lower() == "true"  # 是否扩展到 C 段
    CIDR_PORTS = os.getenv("WEBINFO_CIDR_PORTS", "top-1000")  # C 段用 top-1000 端口
    CIDR_RATE = int(os.getenv("WEBINFO_CIDR_RATE", "100"))  # C 段限速更保守

    # 路径扫描
    PATH_EXTENSIONS = os.getenv("WEBINFO_PATH_EXT", "php,aspx,jsp")
    PATH_EXCLUDE_STATUS = os.getenv("WEBINFO_PATH_EXCLUDE", "301,302,307,400,403,404,500,501,502,503")
    PATH_MIN_RESPONSE = int(os.getenv("WEBINFO_PATH_MIN_RESP", "500"))

    # 目录
    RESULT_DIR = os.getenv("WEBINFO_RESULT", os.path.join(BASE_DIR, "result"))
    POC_DIR = os.path.join(BASE_DIR, "pocs")
    CACHE_DIR = os.path.join(RESULT_DIR, ".cache")
    DB_PATH = os.path.join(RESULT_DIR, "webinfo.db")

    # Web UI
    WEB_HOST = os.getenv("WEBINFO_WEB_HOST", "127.0.0.1")
    WEB_PORT = int(os.getenv("WEBINFO_WEB_PORT", "8888"))


config = Config()
