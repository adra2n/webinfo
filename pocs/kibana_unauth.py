import requests
from pocs.base import POCBase, POCResult


class KibanaUnauth(POCBase):
    name = "kibana_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            r = requests.get(f"{url}/api/status", timeout=5, verify=False)
            if r.status_code == 200:
                data = r.json()
                if data.get("status", {}).get("overall", {}).get("level") == "available":
                    version = data.get("version", {}).get("number", "unknown")
                    return POCResult(
                        level="High",
                        vuln="Kibana 未授权访问",
                        detail=f"Kibana {version} 无需认证可访问",
                    )
        except Exception:
            pass
        return None
