import subprocess
from pocs.base import POCBase, POCResult
from utils.output import log


class RsyncUnauth(POCBase):
    name = "rsync_unauth"

    def check(self, host: str, port: int) -> POCResult | None:
        try:
            result = subprocess.run(
                ["rsync", "--list-only", f"rsync://{host}:{port}/"],
                capture_output=True, text=True, timeout=10,
            )
            output = result.stdout + result.stderr
            if "drwx" in output or "modules" in output.lower():
                return POCResult(
                    level="High",
                    vuln="Rsync 未授权访问",
                    detail=f"rsync://{host}:{port}/ 可列目录",
                )
        except Exception:
            pass
        return None
