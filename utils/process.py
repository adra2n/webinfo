import subprocess
import shlex
from utils.output import log


def run_cmd(args: list[str], timeout: int = 300, shell: bool = False) -> subprocess.CompletedProcess:
    """安全调用子进程，默认不用 shell=True"""
    log.debug(f"exec: {' '.join(args) if not shell else args}")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=shell,
        )
        if result.returncode != 0 and result.stderr:
            log.debug(f"stderr: {result.stderr[:500]}")
        return result
    except subprocess.TimeoutExpired:
        log.warning(f"command timed out after {timeout}s: {args[0] if isinstance(args, list) else args}")
        return subprocess.CompletedProcess(args=args, returncode=-1, stdout="", stderr="timeout")
    except FileNotFoundError:
        log.error(f"command not found: {args[0] if isinstance(args, list) else args}")
        return subprocess.CompletedProcess(args=args, returncode=-1, stdout="", stderr="not found")
    except Exception as e:
        log.error(f"exec failed: {e}")
        return subprocess.CompletedProcess(args=args, returncode=-1, stdout="", stderr=str(e))


def run_nmap(target: str, ports: str, extra_args: list[str] | None = None, timeout: int = 600) -> str:
    """nmap 专用封装，返回 stdout"""
    cmd = ["nmap", "-sV", "-T4", "--open", "--script=banner", "-p", ports, target]
    if extra_args:
        cmd.extend(extra_args)
    result = run_cmd(cmd, timeout=timeout)
    return result.stdout


def run_masscan(ips_file: str, ports: str, rate: int, output: str, timeout: int = 3600) -> str:
    """masscan 专用封装，返回输出文件路径"""
    cmd = [
        "masscan", "-p", ports,
        f"--rate={rate}",
        "--source-port", "53",
        "--wait", "3",
        "-iL", ips_file,
        "-oJ", output,
    ]
    run_cmd(cmd, timeout=timeout)
    return output
