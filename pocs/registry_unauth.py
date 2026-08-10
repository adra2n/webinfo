import requests
from pocs.base import POCBase, POCResult


class RegistryUnauth(POCBase):
    name = "docker_registry_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            # Docker Registry v2 API
            r = requests.get(f"{url}/v2/_catalog", timeout=5, verify=False)
            if r.status_code == 200 and "repositories" in r.text:
                return POCResult(
                    level="High",
                    vuln="Docker Registry 未授权访问",
                    detail=f"GET {url}/v2/_catalog 返回镜像列表",
                )
            # Docker Registry v1 API
            r2 = requests.get(f"{url}/v1/search", timeout=5, verify=False)
            if r2.status_code == 200 and "results" in r2.text:
                return POCResult(
                    level="High",
                    vuln="Docker Registry 未授权访问",
                    detail=f"GET {url}/v1/search 返回搜索结果",
                )
        except Exception:
            pass
        return None
