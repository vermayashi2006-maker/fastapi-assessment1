from enum import Enum
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr

# --- TASK 1 ENUMS & MODELS ---
class ItemStatus(str, Enum):
    LOST = "Lost"
    FOUND = "Found"
    RETURNED = "Returned"

class ItemBase(SQLModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=3)
    category: str = Field(min_length=1)
    location: str = Field(min_length=1)
    reported_by: str = Field(min_length=1)
    status: ItemStatus = Field(default=ItemStatus.LOST)

class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int


# --- TASK 2 ENUMS & MODELS ---
class EventStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"

class EventBase(SQLModel):
    title: str = Field(min_length=1)
    venue: str = Field(min_length=1)
    capacity: int = Field(gt=0)
    organizer: str = Field(min_length=1)
    status: EventStatus = Field(default=EventStatus.OPEN)

class Event(EventBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reservations: List["Reservation"] = Relationship(back_populates="event")

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

class ReservationBase(SQLModel):
    student_name: str = Field(min_length=1)
    roll_number: str = Field(min_length=1)
    email: EmailStr

class Reservation(ReservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    event: Optional[Event] = Relationship(back_populates="reservations")

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    event_id: int

class AvailabilityResponse(SQLModel):
    capacity: int
    booked: int
    remaining: int