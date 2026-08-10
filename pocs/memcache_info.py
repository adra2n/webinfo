import socket
from pocs.base import POCBase, POCResult


class MemcacheInfo(POCBase):
    name = "memcache_info"

    def check(self, host: str, port: int) -> POCResult | None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, int(port)))
            s.send(b"version\r\n")
            data = s.recv(1024).decode(errors="ignore")
            s.close()
            if "VERSION" in data:
                version = data.strip().split()[-1] if len(data.strip().split()) > 1 else ""
                return POCResult(
                    level="High",
                    vuln="Memcached 未授权访问",
                    detail=f"Memcached {version} 无需认证可直接连接",
                )
        except Exception:
            pass
        return None
