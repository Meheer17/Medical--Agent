from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from models import User, UserRole, Query, QueryUrgency
from schemas import QueryCreate, QueryRespond, QueryResponse
from dependencies import get_current_active_user, get_patient_user, get_doctor_user

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
    current_user: User = Depends(get_patient_user),
    db: Session = Depends(get_db)
):
    """
    Create a new query to send to linked doctor
    
    - **query_text**: Your question or message (1-1000 characters)
    - **urgency**: Priority level - low, medium, or high
    
    Note: You must be linked to a doctor first
    """
    # Check if patient has linked doctor
    if not current_user.linked_doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must link to a doctor first before sending queries"
        )
    
    # Verify linked doctor exists and is active
    doctor = db.query(User).filter(
        User.id == current_user.linked_doctor_id,
        User.role == UserRole.DOCTOR,
        User.is_active == True
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your linked doctor is no longer available"
        )
    
    # Create query
    query = Query(
        patient_id=current_user.id,
        doctor_id=current_user.linked_doctor_id,
        query_text=query_data.query_text,
        urgency=query_data.urgency
    )
    
    db.add(query)
    db.commit()
    db.refresh(query)
    
    return query


@router.get(
    "",
    response_model=list[QueryResponse],
    summary="Get my queries",
    description="Get all queries sent/received by current user"
)
async def get_my_queries(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all queries
    
    - **For patients**: Returns queries you've sent to doctors
    - **For doctors**: Returns queries patients have sent to you
    """
    if current_user.role == UserRole.PATIENT:
        queries = db.query(Query).filter(
            Query.patient_id == current_user.id
        ).order_by(Query.created_at.desc()).all()
    elif current_user.role == UserRole.DOCTOR:
        queries = db.query(Query).filter(
            Query.doctor_id == current_user.id
        ).order_by(Query.created_at.desc()).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view queries"
        )
    
    return queries


@router.get(
    "/{query_id}",
    response_model=QueryResponse,
    summary="Get query details",
    description="Get details of a specific query"
)
async def get_query(
    query_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific query
    
    You can only view queries you're involved in
    """
    query = db.query(Query).filter(Query.id == query_id).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check access: patient can view their own queries, doctor can view queries sent to them
    if current_user.role == UserRole.PATIENT:
        if query.patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own queries"
            )
    elif current_user.role == UserRole.DOCTOR:
        if query.doctor_id != current_user.id:
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
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Respond to a patient's query
    
    - **response_text**: Your response (1-1000 characters)
    
    Note: Each query can only be responded to once. After responding, no more messages can be sent on this query.
    """
    query = db.query(Query).filter(Query.id == query_id).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Check if query is for this doctor
    if query.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This query is not for you"
        )
    
    # Check if already responded
    if query.is_responded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This query has already been responded to"
        )
    
    # Add response
    query.response_text = response_data.response_text
    query.is_responded = True
    query.responded_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(query)
    
    return query


@router.get(
    "/pending/count",
    tags=["queries"],
    summary="Count pending queries",
    description="Get count of queries waiting for response (doctors only)"
)
async def get_pending_count(
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Get count of pending queries for this doctor
    """
    pending_count = db.query(Query).filter(
        Query.doctor_id == current_user.id,
        Query.is_responded == False
    ).count()
    
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
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Get all queries waiting for your response
    """
    queries = db.query(Query).filter(
        Query.doctor_id == current_user.id,
        Query.is_responded == False
    ).order_by(Query.created_at).all()
    
    return queries
