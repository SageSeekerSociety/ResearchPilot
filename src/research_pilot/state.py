from dataclasses import dataclass, field
from typing import List, Dict, Any
from arxiv import Result

@dataclass(kw_only=True)
class State:
    question: str = field(default=None)
    keywords: str = field(default=None)
    search_results: List[Result] = field(default_factory=list, repr=False)
    selected_papers: List[Result] = field(default_factory=list, repr=False)
    selected_paper_contents: List[str] = field(default_factory=list)
    answer: str = field(default=None)
    messages: List[Dict[str, Any]] = field(default_factory=list)
