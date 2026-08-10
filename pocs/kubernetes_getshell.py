import requests
from pocs.base import POCBase, POCResult


class KubernetesGetshell(POCBase):
    name = "kubernetes_getshell"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            # 检查 dashboard 是否可访问
            r = requests.get(f"{url}/api/v1/namespace/default/pods", timeout=5, verify=False)
            if r.status_code == 200 and "items" in r.text:
                return POCResult(
                    level="Critical",
                    vuln="Kubernetes Dashboard 未授权 + Pod 创建",
                    detail=f"可访问 {url}/api/v1/namespace/default/pods",
                )
        except Exception:
            pass
        return None
