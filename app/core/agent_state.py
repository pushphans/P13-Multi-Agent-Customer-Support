from typing import Annotated, TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'add_messages' ensures worker outputs get merged safely without overwriting
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Boss batayega kin kin workers ko parallel fire karna hai
    next_workers: List[str]