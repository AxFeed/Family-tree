from datetime import date
from typing import Optional, List
from sqlmodel import SQLModel
from models import TypeLien


class PrenomCreate(SQLModel):
    prenom: str

class PrenomRead(SQLModel):
    id: int
    prenom: str

class NomCreate(SQLModel):
    nom: str

class NomRead(SQLModel):
    id: int
    nom: str

class LienParenteCreate(SQLModel):
    id_parent: int
    type_lien: TypeLien = TypeLien.BIOLOGIQUE

class LienParenteRead(SQLModel):
    id: int
    id_enfant: int
    id_parent: int
    type_lien: TypeLien

class PersonneCreate(SQLModel):
    prenoms: List[str] = []
    noms: List[str] = []
    date_naissance: Optional[date] = None
    date_mort: Optional[date] = None
    parents: List[LienParenteCreate] = []

class PersonneUpdate(SQLModel):
    prenoms: Optional[List[str]] = None
    noms: Optional[List[str]] = None
    date_naissance: Optional[date] = None
    date_mort: Optional[date] = None
    parents: List[LienParenteRead] = []
    enfants: List[LienParenteRead] = []

class PersonneRead(SQLModel):
    id: int
    date_naissance: Optional[date] = None
    date_mort: Optional[date] = None
    prenoms: List[PrenomRead] = []
    noms: List[NomRead] = []
    parents: List[LienParenteRead] = []
    enfants: List[LienParenteRead] = []

class CoupleCreate(SQLModel):
    id_personne_1: int
    id_personne_2: int

class CoupleRead(SQLModel):
    id: int
    id_personne_1: int
    id_personne_2: int