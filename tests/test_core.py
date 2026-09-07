from src.main import build_registry
from src.state.research_state import ResearchState
from src.tools.dispatcher import ToolDispatcher
import logging

def test_unknown_tool():
    d=ToolDispatcher(build_registry(),ResearchState("x","x"),logging.getLogger("test"),5)
    r=d.execute("does_not_exist",{}, {"read"})
    assert r["error_type"]=="unknown_tool"

def test_tool_schema_rejects_extra():
    d=ToolDispatcher(build_registry(),ResearchState("x","x"),logging.getLogger("test"),5)
    r=d.execute("search_information",{"query":"security","max_results":3,"evil":"x"},{"read"})
    assert r["error_type"]=="validation"

def test_calculation_is_bounded():
    d=ToolDispatcher(build_registry(),ResearchState("x","x"),logging.getLogger("test"),5)
    r=d.execute("calculate_metric",{"operation":"sum","values":[2,3]},{"compute"})
    assert r["result"]==5
