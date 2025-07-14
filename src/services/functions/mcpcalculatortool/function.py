import json
import azure.functions as func
from .orchestrator import Orchestrator
from .properties import tool_properties


bp_1 = func.Blueprint()

@bp_1.function_name(name="mcpcalculator")
@bp_1.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="calculator",
    description="Performs a simple addition of two integers.",
    toolProperties=json.dumps([prop.to_dict() for prop in tool_properties])
)
def main(context) -> str:
    content = json.loads(context)
    args = content.get("arguments", {})

    return Orchestrator.run(**args)
