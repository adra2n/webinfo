import requests
from pocs.base import POCBase, POCResult


class KubernetesAuth(POCBase):
    name = "kubernetes_auth"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            r = requests.get(f"{url}/api/v1/namespaces", timeout=5, verify=False)
            if r.status_code == 200 and "items" in r.text:
                return POCResult(
                    level="Critical",
                    vuln="Kubernetes API 未授权访问",
                    detail=f"GET {url}/api/v1/namespaces 返回命名空间列表",
                )
            r2 = requests.get(f"{url}/version", timeout=5, verify=False)
            if r2.status_code == 200 and "gitVersion" in r2.text:
                return POCResult(
                    level="High",
                    vuln="Kubernetes API 版本泄露",
                    detail=f"GET {url}/version 返回版本信息",
                )
        except Exception:
            pass
        return None
