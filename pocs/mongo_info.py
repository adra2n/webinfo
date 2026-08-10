import socket
from pocs.base import POCBase, POCResult


class MongoInfo(POCBase):
    name = "mongo_info"

    def check(self, host: str, port: int) -> POCResult | None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, int(port)))
            # MongoDB isMaster command
            request = b"\x39\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xdd\x07\x00\x00\x01\x00\x00\x00\x21\x00\x00\x00\x02\x69\x73\x4d\x61\x73\x74\x65\x72\x00\x01\x00\x00\x00\x00"
            s.send(request)
            data = s.recv(4096)
            s.close()
            if len(data) > 50:
                text = data.decode(errors="ignore")
                if "maxBsonObjectSize" in text or "maxWriteBatchSize" in text:
                    return POCResult(
                        level="High",
                        vuln="MongoDB 未授权访问",
                        detail="MongoDB isMaster 命令可直接执行",
                    )
        except Exception:
            pass
        return None
