from dataclasses import dataclass
from typing import Any, Callable
from pydantic import TypeAdapter
import inspect

@dataclass
class Tool:
    # A registered tool -  wrap a python function with its metadat
    name: str
    description: str
    function: Callable
    schema: dict

class ToolRegistry:
    # Holds tools, exposes their schema and dispatches incoming calls
    def __init__(self) -> None:
        # index tool by name for a 0(1) lookup
        self._tools: dict[str, Tool] = {}

    def register(self, tool:Tool) -> None:
        self._tools[tool.name] = tool

    def get_schemas(self) -> list[dict]:

        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.schema
                },                
            }
            for t in self._tools.values()
        ]
    
    def dispatch(self, name: str, arguments: dict[str, Any]) -> str:
        if name not in self._tools:
            return f"error: Unknown tool {name}"

        try:
            result  = self._tools[name].function(**arguments)
            return str(result)
        except Exception as e:
            return f"error: {type(e).__name__}: {e}"

registry = ToolRegistry()

def tool(func: Callable) -> Callable:

    name = func.__name__
    description = inspect.getdoc(func) or ""

    schema = TypeAdapter(func).json_schema()

    registry.register(Tool(
        name=name,
        description=description,
        function=func,
        schema=schema
    ))
    return func


