import socket
from pocs.base import POCBase, POCResult


class KafkaInfo(POCBase):
    name = "kafka_info"

    def check(self, host: str, port: int) -> POCResult | None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, int(port)))
            # Kafka broker request: ApiKey=18 (Metadata)
            request = b"\x00\x12\x00\x12\x00\x00\x00\x00\x00\x01\x00\x06test\x00\x00\x00\x01\x00\x00"
            s.send(request)
            data = s.recv(4096)
            s.close()
            if len(data) > 10:
                return POCResult(
                    level="Info",
                    vuln="Kafka 端口开放且可连接",
                    detail=f"Kafka broker 响应了 Metadata 请求",
                )
        except Exception:
            pass
        return None
