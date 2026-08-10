import requests
from pocs.base import POCBase, POCResult


class DjangoDebug(POCBase):
    name = "django_debug"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        paths = ["/", "/admin/", "/static/admin/"]
        for path in paths:
            try:
                r = requests.get(f"{url}{path}", timeout=5, verify=False, allow_redirects=False)
                if r.status_code == 500 and "traceback" in r.text.lower() and "django" in r.text.lower():
                    return POCResult(
                        level="Medium",
                        vuln="Django Debug Mode 开启",
                        detail=f"GET {url}{path} 返回调试页面",
                    )
            except Exception:
                continue
        return None
