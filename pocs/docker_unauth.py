import requests
from pocs.base import POCBase, POCResult


class DockerUnauth(POCBase):
    name = "docker_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            r = requests.get(f"{url}/", timeout=5, verify=False, allow_redirects=False)
            if r.status_code == 404:
                r2 = requests.get(f"{url}/containers/json", timeout=5, verify=False, allow_redirects=False)
                if r2.text and "Image" in r2.text:
                    return POCResult(level="High", vuln="Docker Remote API 未授权访问", detail=f"GET {url}/containers/json 返回容器列表")
        except Exception:
            pass
        return None
