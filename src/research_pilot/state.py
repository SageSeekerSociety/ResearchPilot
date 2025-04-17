from dataclasses import dataclass, field

@dataclass(kw_only=True)
class State:
    content: str = field(default=None)
