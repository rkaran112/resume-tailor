from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.contact import ContactInfo

ModelT = TypeVar("ModelT")

CONTACT_INFO_ID = 1


def get_or_404(db: Session, model: type[ModelT], obj_id: int) -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {obj_id} not found")
    return obj


def get_or_create_contact_info(db: Session) -> ContactInfo:
    contact = db.get(ContactInfo, CONTACT_INFO_ID)
    if contact is None:
        contact = ContactInfo(
            id=CONTACT_INFO_ID, name="", email="", phone="", location="", links=[]
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact
