import socket
from pocs.base import POCBase, POCResult


class ZookeeperUnauth(POCBase):
    name = "zookeeper_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, int(port)))
            # 发送四字命令 stats
            s.send(b"stats")
            data = s.recv(4096).decode(errors="ignore")
            s.close()
            if "zk_version" in data.lower() or "zk_server_state" in data.lower():
                return POCResult(
                    level="High",
                    vuln="ZooKeeper 未授权访问",
                    detail="ZooKeeper 四字命令 stats 可直接执行",
                )
        except Exception:
            pass
        return None
