import requests
from pocs.base import POCBase, POCResult


class ConsulExec(POCBase):
    name = "consul_exec"

    def check(self, host: str, port: int) -> POCResult | None:
        url = self.build_url(host, port)
        try:
            r = requests.get(f"{url}/v1/agent/self", timeout=5, verify=False)
            if r.status_code == 200 and len(r.text) > 0 and "Config" in r.text:
                return POCResult(
                    level="High",
                    vuln="Consul 未授权访问",
                    detail=f"GET {url}/v1/agent/self 返回 Agent 配置信息",
                )
        except Exception:
            pass
        return None
