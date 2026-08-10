from dataclasses import dataclass, field


@dataclass
class POCResult:
    level: str
    vuln: str
    detail: str = ""


class POCBase:
    """所有 POC 的基类"""

    name: str = "unknown"

    def check(self, host: str, port: int) -> POCResult | None:
        raise NotImplementedError

    def build_url(self, host: str, port: int) -> str:
        scheme = "https" if port in (443, 8443) else "http"
        return f"{scheme}://{host}:{port}"
