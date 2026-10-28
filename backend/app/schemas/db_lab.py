# TransitMatrix - Database Lab Pydantic Schemas

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class QueryCatalogItem(BaseModel):
    query_id: str
    title: str
    category: str
    description: str
    sql_statement: str


class QueryExecutionResponse(BaseModel):
    query_id: str
    title: str
    sql_statement: str
    execution_time_ms: float
    row_count: int
    columns: List[str]
    rows: List[Dict[str, Any]]
    explain_plan: Optional[List[Dict[str, Any]]] = None
