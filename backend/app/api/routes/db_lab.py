# TransitMatrix - Database Lab Endpoints

from fastapi import APIRouter, Depends
from typing import List
from app.schemas.db_lab import QueryCatalogItem, QueryExecutionResponse
from app.services.db_lab_service import DbLabService
from app.api.deps import require_roles

router = APIRouter(prefix="/database-lab", tags=["Database Lab"])


@router.get("/catalog", response_model=List[QueryCatalogItem])
def get_query_catalog(current_user=Depends(require_roles("ADMIN", "STAFF"))):
    """
    Returns the catalog of 21 advanced relational SQL queries.
    """
    return DbLabService.get_query_catalog()


@router.get("/execute/{query_id}", response_model=QueryExecutionResponse)
def execute_query(
    query_id: str,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Executes a predefined SQL demonstration query against live MySQL 8.0+ and returns
    execution duration, row counts, resulting records, and EXPLAIN query plan.
    """
    return DbLabService.execute_query(query_id)
