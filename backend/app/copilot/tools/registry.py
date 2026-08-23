"""Tool registry - maps tool names to functions with schemas."""
from typing import Callable, Dict, Any, List

TOOL_REGISTRY: Dict[str, dict] = {}


def register_tool(name: str, description: str, parameters: dict):
    """Decorator to register a copilot tool."""
    def decorator(func: Callable):
        TOOL_REGISTRY[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "function": func,
        }
        return func
    return decorator


def get_tool_schemas() -> List[dict]:
    """Get all tool schemas for the AI prompt."""
    schemas = []
    for tool_name, tool_info in TOOL_REGISTRY.items():
        schemas.append({
            "name": tool_info["name"],
            "description": tool_info["description"],
            "parameters": tool_info["parameters"],
        })
    return schemas


def call_tool(name: str, db, org_id: int, **kwargs) -> Any:
    """Execute a registered tool with organization isolation."""
    if name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {name}"}
    tool = TOOL_REGISTRY[name]
    try:
        result = tool["function"](db=db, org_id=org_id, **kwargs)
        return result
    except Exception as e:
        return {"error": f"Tool {name} failed: {str(e)}"}
