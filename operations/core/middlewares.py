import sqltap
from starlette.types import ASGIApp, Receive, Scope, Send


class SqltapProfilerMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        profiler = sqltap.start()
        response = await self.app(scope, receive, send)
        statistics = profiler.collect()
        sqltap.report(statistics, filename="profiler.txt", report_format="text")
        return response
