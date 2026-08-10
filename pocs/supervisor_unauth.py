import requests
from pocs.base import POCBase, POCResult


class SupervisorUnauth(POCBase):
    name = "supervisor_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            r = requests.get(f"{url}/RPC2", timeout=5, verify=False)
            if r.status_code == 200 and "supervisor" in r.text.lower():
                return POCResult(
                    level="High",
                    vuln="Supervisor 未授权访问",
                    detail=f"GET {url}/RPC2 返回 Supervisor XML-RPC 接口",
                )
        except Exception:
            pass
        return None
