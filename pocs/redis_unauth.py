import socket
from pocs.base import POCBase, POCResult


class RedisUnauth(POCBase):
    name = "redis_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, int(port)))
            s.send(b"INFO\r\n")
            data = s.recv(1024).decode(errors="ignore")
            s.close()
            if "redis_version" in data:
                version = ""
                for line in data.split("\n"):
                    if "redis_version" in line:
                        version = line.split(":")[-1].strip()
                        break
                return POCResult(
                    level="High",
                    vuln="Redis 未授权访问",
                    detail=f"Redis {version} 无需认证可直接连接",
                )
        except Exception:
            pass
        return None
