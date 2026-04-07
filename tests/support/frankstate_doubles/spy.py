from typing import Any


class SpyRunnable:
    def __init__(self, sync_result: Any = None, async_result: Any = None):
        self.sync_result = sync_result
        self.async_result = async_result if async_result is not None else sync_result
        self.calls: list[tuple[str, Any]] = []

    def _resolve_result(self, result: Any, payload: Any) -> Any:
        return result(payload) if callable(result) else result

    def invoke(self, payload: Any) -> Any:
        self.calls.append(("invoke", payload))
        return self._resolve_result(self.sync_result, payload)

    async def ainvoke(self, payload: Any) -> Any:
        self.calls.append(("ainvoke", payload))
        return self._resolve_result(self.async_result, payload)
