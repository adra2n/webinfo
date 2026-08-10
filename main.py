import os
import sys
import argparse
from config import config
from core.db import ScanDB
from core.context import ScanContext
from core.workflow import Workflow, Step, ALL_STEPS
from core.reporter import export_to_excel, export_summary
from utils.output import log
from utils.banner import showbanner


def parse_args():
    parser = argparse.ArgumentParser(
        description="webinfo - 自动化信息收集工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py -d example.com --all          # 一键全扫
  python main.py -d example.com -dm            # 仅子域名枚举
  python main.py -d example.com -dm -host      # 子域名 + 资产提取
  python main.py -d example.com -sc            # 端口扫描（分层）
  python main.py -d example.com -hack          # POC 漏洞扫描
  python main.py -d example.com --export xlsx  # 导出 Excel
  python main.py -d example.com --summary      # 查看摘要
        """,
    )
    parser.add_argument("-d", "--domain", help="目标域名")
    parser.add_argument("--all", action="store_true", help="执行全部步骤")
    parser.add_argument("-dm", action="store_true", help="子域名枚举")
    parser.add_argument("-host", action="store_true", help="资产提取")
    parser.add_argument("-sc", action="store_true", help="分层端口扫描")
    parser.add_argument("-dr", action="store_true", help="路径扫描")
    parser.add_argument("-hack", action="store_true", help="POC 漏洞扫描")
    parser.add_argument("--export", choices=["xlsx"], help="导出 Excel")
    parser.add_argument("--summary", action="store_true", help="查看扫描摘要")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        log.setLevel("DEBUG")

    if not args.domain:
        log.error("请指定目标域名 (-d DOMAIN)")
        sys.exit(1)

    showbanner()

    # 导出/摘要模式
    if args.export or args.summary:
        with ScanDB() as db:
            if args.export:
                output = os.path.join(config.RESULT_DIR, f"{args.domain}.xlsx")
                export_to_excel(db.db_path, output)
            if args.summary:
                print(export_summary(db.db_path, args.domain))
        return

    # 确定要执行的步骤
    steps = []
    if args.all:
        steps = ALL_STEPS
    else:
        if args.dm:
            steps.append(Step.DOMAIN)
        if args.host:
            steps.append(Step.ASSET)
        if args.sc:
            steps.append(Step.PORT)
        if args.dr:
            steps.append(Step.PATH)
        if args.hack:
            steps.append(Step.VULN)

    if not steps:
        log.error("请指定要执行的步骤 (--all / -dm / -host / -sc / -dr / -hack)")
        sys.exit(1)

    # 执行扫描
    with ScanDB() as db:
        ctx = ScanContext(args.domain, db)
        wf = Workflow(ctx)
        wf.run(steps)

        # 打印摘要
        print(export_summary(db.db_path, args.domain))


if __name__ == "__main__":
    main()
