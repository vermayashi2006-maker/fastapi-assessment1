from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import (
    Event, EventCreate, EventResponse, EventStatus,
    Reservation, ReservationCreate, ReservationResponse, AvailabilityResponse
)

router = APIRouter(tags=["Task 2 - Event Reservation"])

# --- EVENT ENDPOINTS ---
@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, session: Session = Depends(get_session)):
    db_event = Event.model_validate(event)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.get("/events", response_model=List[EventResponse])
def read_events(session: Session = Depends(get_session)):
    return session.exec(select(Event)).all()

@router.get("/events/{event_id}", response_model=EventResponse)
def read_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventCreate, session: Session = Depends(get_session)):
    db_event = session.get(Event, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    event_data = event_update.model_dump(exclude_unset=True)
    for key, value in event_data.items():
        setattr(db_event, key, value)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    return db_event

@router.delete("/events/{event_id}")
def delete_event(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    session.delete(event)
    session.commit()
    return {"message": "Event deleted successfully"}

# --- RESERVATION ENDPOINTS ---
@router.post("/events/{event_id}/reserve", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(event_id: int, reservation: ReservationCreate, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.status == EventStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Cannot reserve seats for a Closed event")
    
    booked_count = len(session.exec(select(Reservation).where(Reservation.event_id == event_id)).all())
    if booked_count >= event.capacity:
        raise HTTPException(status_code=400, detail="Event capacity is full")
    
    db_reservation = Reservation(**reservation.model_dump(), event_id=event_id)
    session.add(db_reservation)
    session.commit()
    session.refresh(db_reservation)
    return db_reservation

@router.get("/events/{event_id}/reservations", response_model=List[ReservationResponse])
def get_event_reservations(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return session.exec(select(Reservation).where(Reservation.event_id == event_id)).all()

@router.get("/events/{event_id}/availability", response_model=AvailabilityResponse)
def get_event_availability(event_id: int, session: Session = Depends(get_session)):
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    booked = len(session.exec(select(Reservation).where(Reservation.event_id == event_id)).all())
    remaining = event.capacity - booked
    return AvailabilityResponse(capacity=event.capacity, booked=booked, remaining=remaining)

@router.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int, session: Session = Depends(get_session)):
    res = session.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reservation not found")
    session.delete(res)
    session.commit()
    return {"message": "Reservation cancelled successfully"}