from fastapi import HTTPException
from sqlmodel import Session, select

from models import LienParente, TypeLien
from datetime import date
from typing import Optional


def verifier_dates(date_naissance: Optional[date], date_mort: Optional[date]) -> None:
    if date_naissance and date_mort and date_mort < date_naissance:
        raise HTTPException(status_code=422, detail="La date de décès ne peut pas être avant la date de naissance.")


def verifier_parents_biologique(session: Session, id_enfant: int, type_lien: TypeLien) -> None:
    if type_lien != TypeLien.BIOLOGIQUE:
        return
    count = len(session.exec(select(LienParente).where(
        LienParente.id_enfant == id_enfant,
        LienParente.type_lien == TypeLien.BIOLOGIQUE
    )).all())
    if count >= 2:
        raise HTTPException(status_code=422, detail="Maximum 2 parents biologiques.")


def verifier_cycle_genealogique(session: Session, id_enfant: int, id_parent: int) -> None:
    visites, file = set(), [id_parent]
    while file:
        courant = file.pop(0)
        if courant == id_enfant:
            raise HTTPException(status_code=422, detail="Cycle généalogique bizarre détecté.")
        if courant in visites:
            continue
        visites.add(courant)
        file.extend(session.exec(
            select(LienParente.id_parent).where(LienParente.id_enfant == courant)
        ).all())