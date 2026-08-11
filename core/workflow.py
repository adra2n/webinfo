from enum import Enum
from core.context import ScanContext
from utils.output import log


class Step(Enum):
    DOMAIN = "dm"
    ASSET = "host"
    PORT = "sc"
    PATH = "dr"
    VULN = "hack"


ALL_STEPS = [Step.DOMAIN, Step.ASSET, Step.PORT, Step.PATH, Step.VULN]

STEP_NAMES = {
    Step.DOMAIN: "子域名枚举",
    Step.ASSET: "资产提取",
    Step.PORT: "端口扫描",
    Step.PATH: "路径扫描",
    Step.VULN: "漏洞扫描",
}


class Workflow:
    def __init__(self, ctx: ScanContext):
        self.ctx = ctx

    def _print_progress(self, current_step: Step, steps: list[Step], done: int):
        """打印整体扫描进度"""
        total = len(steps)
        bar_length = 30
        progress = done / total if total > 0 else 0
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        step_name = STEP_NAMES.get(current_step, current_step.value)
        print(f"\n[*] 扫描进度: |{bar}| {done}/{total} ({int(progress*100)}%) - 当前: {step_name}\n")

    def run(self, steps: list[Step]):
        # 设置日志收集器的 domain
        for handler in log.handlers:
            if hasattr(handler, "set_domain"):
                handler.set_domain(self.ctx.domain)

        done_count = 0
        for i, step in enumerate(steps):
            if self.ctx.is_step_done(step.value):
                log.info(f"跳过 {STEP_NAMES.get(step, step.value)}（已完成）")
                done_count += 1
                continue
            
            # 显示进度
            self._print_progress(step, steps, done_count)
            
            log.info(f"执行步骤: {STEP_NAMES.get(step, step.value)}")
            self._execute(step)
            self.ctx.mark_step_done(step.value)
            done_count += 1

        # 清理 handler 的 domain
        for handler in log.handlers:
            if hasattr(handler, "set_domain"):
                handler.set_domain(None)

    def _execute(self, step: Step):
        from scanners import subdomain, asset, port, path, vuln, analyzer

        handlers = {
            Step.DOMAIN: subdomain.scan,
            Step.ASSET: asset.scan,
            Step.PORT: port.scan,
            Step.PATH: path.scan,
            Step.VULN: vuln.scan,
        }

        handler = handlers.get(step)
        if handler:
            try:
                handler(self.ctx)
            except Exception as e:
                log.error(f"步骤 {STEP_NAMES.get(step, step.value)} 执行失败: {e}")
                raise

        # 端口扫描后自动执行分析
        if step == Step.PORT:
            try:
                analyzer.scan(self.ctx)
            except Exception as e:
                log.warning(f"分析步骤失败: {e}")
