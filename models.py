from datetime import date
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class TypeLien(str, Enum):
    BIOLOGIQUE  = "BIOLOGIQUE"
    ADOPTIF     = "ADOPTIF"
    BEAU_PARENT = "BEAU_PARENT"


class Personne(SQLModel, table=True):
    __tablename__ = "Personne"

    id: Optional[int] = Field(default=None, primary_key=True)
    date_naissance: Optional[date] = Field(default=None)
    date_mort: Optional[date] = Field(default=None)
    prenoms: List["Prenom"] = Relationship(back_populates="personne", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    noms: List["Nom"] = Relationship(back_populates="personne", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class Prenom(SQLModel, table=True):
    __tablename__ = "Prenom"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_personne: int = Field(foreign_key="Personne.id")
    prenom: str = Field(max_length=255)

    personne: Optional["Personne"] = Relationship(back_populates="prenoms")


class Nom(SQLModel, table=True):
    __tablename__ = "Nom"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_personne: int = Field(foreign_key="Personne.id")
    nom: str = Field(max_length=255)

    personne: Optional["Personne"] = Relationship(back_populates="noms")


class LienParente(SQLModel, table=True):
    __tablename__ = "LienParente"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_enfant: int = Field(foreign_key="Personne.id")
    id_parent: int = Field(foreign_key="Personne.id")
    type_lien: TypeLien = Field(default=TypeLien.BIOLOGIQUE)


class Couple(SQLModel, table=True):
    __tablename__ = "Couple"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_personne_1: int = Field(foreign_key="Personne.id")
    id_personne_2: int = Field(foreign_key="Personne.id")