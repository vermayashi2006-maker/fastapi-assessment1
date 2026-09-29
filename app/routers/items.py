from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Item, ItemCreate, ItemResponse, ItemStatus

router = APIRouter(tags=["Task 1 - Lost & Found"])

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/items", response_model=List[ItemResponse])
def read_items(session: Session = Depends(get_session)):
    return session.exec(select(Item)).all()

@router.get("/items/status/{status_val}", response_model=List[ItemResponse])
def read_items_by_status(status_val: ItemStatus, session: Session = Depends(get_session)):
    return session.exec(select(Item).where(Item.status == status_val)).all()

@router.get("/items/category/{category_val}", response_model=List[ItemResponse])
def read_items_by_category(category_val: str, session: Session = Depends(get_session)):
    return session.exec(select(Item).where(Item.category.ilike(f"%{category_val}%"))).all()

@router.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemCreate, session: Session = Depends(get_session)):
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    item_data = item_update.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    session.delete(item)
    session.commit()
    return {"message": "Item deleted successfully"}