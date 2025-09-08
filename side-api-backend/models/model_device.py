from pydantic import BaseModel
from typing import Optional, List


class Device(BaseModel):
    id: str
    label: Optional[str]
    role: Optional[str]
    ip: Optional[str]
    port: Optional[int]
    first_seen: Optional[str]
    last_seen: Optional[str]


class Link(BaseModel):
    source: str
    target: str
    relation: str


class GraphResponse(BaseModel):
    nodes: List[Device]
    links: List[Link]
