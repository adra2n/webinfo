import random
import re
import urllib3
import ssl
import requests
from bs4 import BeautifulSoup
from utils.output import log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


def random_headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }


def make_session(verify: bool = False) -> requests.Session:
    """创建 HTTP session，按需关闭 SSL 验证（非全局）"""
    session = requests.Session()
    session.verify = verify
    session.headers.update(random_headers())
    return session


def get_info(url: str, timeout: int = 5) -> tuple[str, str, str]:
    """获取 URL 的 headers、body、title"""
    try:
        resp = requests.get(url, headers=random_headers(), timeout=timeout, verify=False, allow_redirects=False)
        content = resp.text
        title = ""
        if resp.status_code in (200, 500):
            try:
                soup = BeautifulSoup(content, "lxml")
                title = soup.title.text.strip() if soup.title else content[:50]
            except Exception:
                title = content[:50]
        return str(resp.headers), content, title
    except requests.exceptions.Timeout:
        return "", "", ""
    except requests.exceptions.ConnectionError:
        return "", "", ""
    except Exception as e:
        log.debug(f"get_info error for {url}: {e}")
        return "", "", ""


def check_rule(rule: str, header: str, body: str, title: str) -> bool:
    """指纹规则匹配"""
    try:
        if 'title="' in rule:
            pattern = re.search(r'title="(.*)"', rule)
            if pattern and pattern.group(1).lower() in title.lower():
                return True
        elif 'body="' in rule:
            pattern = re.search(r'body="(.*)"', rule)
            if pattern and pattern.group(1) in body:
                return True
        elif 'header="' in rule:
            pattern = re.search(r'header="(.*)"', rule)
            if pattern and pattern.group(1) in header:
                return True
    except Exception:
        pass
    return False


def build_url(host: str, port: int) -> str:
    """根据端口号构建 URL"""
    scheme = "https" if port in (443, 8443) else "http"
    return f"{scheme}://{host}:{port}"
