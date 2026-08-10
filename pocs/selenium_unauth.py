import requests
from pocs.base import POCBase, POCResult


class SeleniumUnauth(POCBase):
    name = "selenium_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            r = requests.get(f"{url}/grid/console", timeout=5, verify=False)
            if r.status_code == 200 and "grid" in r.text.lower():
                return POCResult(
                    level="Medium",
                    vuln="Selenium Grid 未授权访问",
                    detail=f"GET {url}/grid/console 返回控制台页面",
                )
            r2 = requests.get(f"{url}/status", timeout=5, verify=False)
            if r2.status_code == 200:
                data = r2.json()
                if data.get("value", {}).get("ready"):
                    return POCResult(
                        level="Medium",
                        vuln="Selenium Grid 未授权访问",
                        detail=f"GET {url}/status 返回 Grid 状态",
                    )
        except Exception:
            pass
        return None
