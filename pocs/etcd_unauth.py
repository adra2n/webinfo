import requests
from pocs.base import POCBase, POCResult


class EtcdUnauth(POCBase):
    name = "etcd_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            r = requests.get(f"{url}/v2/keys/", timeout=5, verify=False)
            if r.status_code == 200 and "nodes" in r.text:
                return POCResult(
                    level="High",
                    vuln="etcd 未授权访问",
                    detail=f"GET {url}/v2/keys/ 返回数据",
                )
        except Exception:
            pass
        return None
