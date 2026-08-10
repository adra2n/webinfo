import os
import importlib.util
import json
from multiprocessing.dummy import Pool as threadpool
from config import config
from core.context import ScanContext
from utils.output import log
from pocs.base import POCBase


def load_pocs() -> list[POCBase]:
    """动态加载 pocs/ 目录下所有 POC 类"""
    pocs = []
    poc_dir = config.POC_DIR
    for fname in os.listdir(poc_dir):
        if fname.startswith("_") or not fname.endswith(".py"):
            continue
        fpath = os.path.join(poc_dir, fname)
        try:
            spec = importlib.util.spec_from_file_location(fname[:-3], fpath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, POCBase)
                    and attr is not POCBase
                ):
                    pocs.append(attr())
        except Exception as e:
            log.warning(f"failed to load POC {fname}: {e}")
    return pocs


def _run_poc(poc: POCBase, host: str, port: int, service: str):
    """单个 POC 执行"""
    try:
        result = poc.check(host, port)
        if result:
            return {
                "host": host,
                "port": port,
                "service": service,
                "level": result.level,
                "vuln": result.vuln,
                "detail": result.detail,
            }
    except Exception as e:
        log.debug(f"POC {poc.name} error on {host}:{port}: {e}")
    return None


def scan(context: ScanContext):
    """对 nmap 服务识别结果执行所有 POC"""
    log.info(f"开始 POC 漏洞扫描")

    # 读取 nmap 服务识别结果
    nmap_file = context.nmap_service_json
    if not os.path.exists(nmap_file):
        # 回退到快速扫描结果
        nmap_file = context.nmap_fast_json
    if not os.path.exists(nmap_file):
        log.error("未找到端口扫描结果，请先执行 -sc")
        return

    targets = []
    with open(nmap_file) as f:
        for line in f:
            line = line.strip().rstrip(",")
            if not line:
                continue
            try:
                js = json.loads(line)
                targets.append(js)
            except json.JSONDecodeError:
                continue

    if not targets:
        log.warning("无端口扫描结果可执行 POC")
        return

    pocs = load_pocs()
    log.info(f"已加载 {len(pocs)} 个 POC，目标 {len(targets)} 个")

    results = []

    def _task(item):
        host = str(item.get("ip", item.get("host", "")))
        port = int(item.get("port", 0))
        service = str(item.get("service", ""))
        for poc in pocs:
            r = _run_poc(poc, host, port, service)
            if r:
                results.append(r)
                log.info(f"[VULN] {host}:{port} - {r['level']} - {r['vuln']}")

    pool = threadpool(config.THREADS)
    pool.map(_task, targets)
    pool.close()
    pool.join()

    # 写入数据库
    for r in results:
        context.db.add_vuln(
            context.scan_id,
            host=r["host"],
            port=r["port"],
            service=r["service"],
            level=r["level"],
            vuln=r["vuln"],
            detail=r.get("detail", ""),
        )

    log.info(f"POC 扫描完成，发现 {len(results)} 个漏洞")
