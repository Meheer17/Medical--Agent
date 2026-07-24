from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import DESCENDING

from database import get_db, get_next_sequence_value
from models import UserRole
from schemas import QueryCreate, QueryRespond, QueryResponse
from dependencies import get_current_active_user, get_patient_user, get_doctor_user, DictWrapper

router = APIRouter(prefix="/api/queries", tags=["queries"])

@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a query",
    description="Patient sends a query to their linked doctor"
)
async def create_query(
    query_data: QueryCreate,
    current_user: DictWrapper = Depends(get_patient_user),
    db = Depends(get_db)
):
    """Create a new query to send to linked doctor"""
    linked_id = current_user.get("linked_doctor_id")
    if not linked_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must link to a doctor first before sending queries"
        )
    
    doctor = await db.users.find_one({
        "id": linked_id,
        "role": UserRole.DOCTOR.value,
        "is_active": True
    })
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your linked doctor is no longer available"
        )
    
    query_id = await get_next_sequence_value("queries")
    now = datetime.now(timezone.utc)
    urgency_val = query_data.urgency.value if hasattr(query_data.urgency, 'value') else str(query_data.urgency)

    query_doc = {
        "id": query_id,
        "patient_id": current_user.id,
        "doctor_id": linked_id,
        "query_text": query_data.query_text,
        "response_text": None,
        "urgency": urgency_val,
        "is_responded": False,
        "created_at": now,
        "responded_at": None
    }
    
    await db.queries.insert_one(query_doc)
    return query_doc

@router.get(
    "",
    response_model=list[QueryResponse],
    summary="Get my queries",
    description="Get all queries sent/received by current user"
)
async def get_my_queries(
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get all queries"""
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if role_val == UserRole.PATIENT.value:
        cursor = db.queries.find({"patient_id": current_user.id}).sort("created_at", DESCENDING)
    elif role_val == UserRole.DOCTOR.value:
        cursor = db.queries.find({"doctor_id": current_user.id}).sort("created_at", DESCENDING)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view queries"
        )
    
    queries = await cursor.to_list(length=1000)
    return queries

@router.get(
    "/pending/count",
    tags=["queries"],
    summary="Count pending queries",
    description="Get count of queries waiting for response (doctors only)"
)
async def get_pending_count(
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get count of pending queries for this doctor"""
    pending_count = await db.queries.count_documents({
        "doctor_id": current_user.id,
        "is_responded": False
    })
    
    return {
        "doctor_id": current_user.id,
        "pending_count": pending_count
    }

@router.get(
    "/pending/list",
    response_model=list[QueryResponse],
    tags=["queries"],
    summary="Get pending queries",
    description="Get all pending queries (doctors only)"
)
async def get_pending_queries(
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get all queries waiting for your response"""
    cursor = db.queries.find({
        "doctor_id": current_user.id,
        "is_responded": False
    }).sort("created_at", DESCENDING)
    
    queries = await cursor.to_list(length=1000)
    return queries

@router.get(
    "/{query_id}",
    response_model=QueryResponse,
    summary="Get query details",
    description="Get details of a specific query"
)
async def get_query(
    query_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get details of a specific query"""
    query = await db.queries.find_one({"id": query_id})
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if role_val == UserRole.PATIENT.value:
        if query["patient_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own queries"
            )
    elif role_val == UserRole.DOCTOR.value:
        if query["doctor_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view queries sent to you"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this query"
        )
    
    return query

@router.post(
    "/{query_id}/respond",
    response_model=QueryResponse,
    summary="Respond to query",
    description="Doctor responds to a patient's query"
)
async def respond_to_query(
    query_id: int,
    response_data: QueryRespond,
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Respond to a patient's query"""
    query = await db.queries.find_one({"id": query_id})
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    if query["doctor_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This query is not for you"
        )
    
    if query.get("is_responded"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This query has already been responded to"
        )
    
    now = datetime.now(timezone.utc)
    await db.queries.update_one(
        {"id": query_id},
        {"$set": {
            "response_text": response_data.response_text,
            "is_responded": True,
            "responded_at": now
        }}
    )
    
    updated_doc = await db.queries.find_one({"id": query_id})
    return updated_doc
