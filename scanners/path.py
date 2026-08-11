import os
import subprocess
import sys
from config import config
from core.context import ScanContext
from utils.output import log


def scan(context: ScanContext):
    """路径扫描（调用 dirsearch）"""
    log.info(f"开始路径扫描: {context.domain}")

    if not os.path.exists(context.hosts_file):
        log.error("未找到 hosts 文件，请先执行 -host")
        return

    path_out = os.path.join(context.cache_dir, "path.csv")

    # 使用项目的 venv Python
    python_exe = "/Users/adrain/Desktop/project/.venv/bin/python"
    if not os.path.exists(python_exe):
        python_exe = sys.executable
    
    # 修复参数格式
    cmd = [
        python_exe, config.DIRSEARCH,
        "--urls-file", context.hosts_file,
        "-e", config.PATH_EXTENSIONS,
        "--timeout=3",
        f"-x {config.PATH_EXCLUDE_STATUS}",
        f"-t {config.THREADS}",
        f"--min-response-size={config.PATH_MIN_RESPONSE}",
        "--random-agent",
        "--no-color",
        "-o", path_out,
        "-O", "csv"
    ]

    log.info(f"执行: {' '.join(cmd[:5])}...")

    # 使用 Popen 异步运行，不读取 stdout 避免阻塞
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 等待进程完成
    proc.wait()

    # 解析 CSV 结果写入数据库
    if os.path.exists(path_out):
        count = 0
        with open(path_out) as f:
            header = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if header is None:
                    header = parts
                    continue
                if len(parts) >= 4:
                    context.db.add_path(
                        context.scan_id,
                        url=parts[0] if len(parts) > 0 else "",
                        status=int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0,
                        content_length=int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                        title=parts[3] if len(parts) > 3 else "",
                    )
                    count += 1
        log.info(f"路径扫描完成，发现 {count} 条路径")
    else:
        log.warning("路径扫描未生成结果")

    context.mark_step_done("dr")
