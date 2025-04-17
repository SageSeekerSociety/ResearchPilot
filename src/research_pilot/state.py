from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(kw_only=True)
class State:
    content: str = field(default=None)
    messages: List[Dict[str, Any]] = field(default_factory=list)
