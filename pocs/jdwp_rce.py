import socket
import struct
from pocs.base import POCBase, POCResult


class JdwpRce(POCBase):
    name = "jdwp_rce"

    def check(self, host: str, port: int) -> POCResult | None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((host, int(port)))

            # JDWP Handshake
            handshake = b"JDWP-Handshake"
            s.send(handshake)
            resp = s.recv(1024)

            if resp == b"JDWP-Handshake":
                # 发送 Command: VM_Version (0x01, 0x01)
                packet = struct.pack(">II", 11, 0) + struct.pack(">BB", 1, 1)
                s.send(packet)
                data = s.recv(1024)
                s.close()
                if len(data) > 20:
                    return POCResult(
                        level="High",
                        vuln="JDWP 远程代码执行",
                        detail=f"JDWP 握手成功，可能实现远程代码执行",
                    )
            s.close()
        except Exception:
            pass
        return None
