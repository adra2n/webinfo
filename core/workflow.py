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


class Workflow:
    def __init__(self, ctx: ScanContext):
        self.ctx = ctx

    def run(self, steps: list[Step]):
        # 设置日志收集器的 domain
        for handler in log.handlers:
            if hasattr(handler, "set_domain"):
                handler.set_domain(self.ctx.domain)

        for step in steps:
            if self.ctx.is_step_done(step.value):
                log.info(f"跳过 {step.value}（已完成）")
                continue
            log.info(f"执行步骤: {step.value}")
            self._execute(step)
            self.ctx.mark_step_done(step.value)

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
                log.error(f"步骤 {step.value} 执行失败: {e}")
                raise

        # 端口扫描后自动执行分析
        if step == Step.PORT:
            try:
                analyzer.scan(self.ctx)
            except Exception as e:
                log.warning(f"分析步骤失败: {e}")
