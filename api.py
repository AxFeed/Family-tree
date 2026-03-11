from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from database import get_session
from models import Personne, Prenom, Nom, LienParente, Couple, TypeLien
import schemas
import contraintes

app = FastAPI()


def getPersonne(session, id_personne):
    personne = session.get(Personne, id_personne)
    if not personne:
        raise HTTPException(status_code=404, detail=f"Personne {id_personne} introuvable.")
    return personne


def verifierContrainteBdd(session):
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        print(f"ERREUR SQL : {e.orig}")  # ← ajoute ça
        raise HTTPException(status_code=409, detail="Contrainte de base de données violée.")


@app.get("/")
def racine():
    return {"message": "BobFamily API opérationnelle", "docs": "/docs"}

@app.get("/personnes/", response_model=List[schemas.PersonneRead])
def lister_personnes(session: Session = Depends(get_session)):
    personnes = session.exec(select(Personne)).all()
    resultat = []
    for personne in personnes:
        prenoms = session.exec(select(Prenom).where(Prenom.id_personne == personne.id)).all()
        noms = session.exec(select(Nom).where(Nom.id_personne == personne.id)).all()
        parents = session.exec(select(LienParente).where(LienParente.id_enfant == personne.id)).all()
        enfants = session.exec(select(LienParente).where(LienParente.id_parent == personne.id)).all()
        resultat.append(schemas.PersonneRead(
            id=personne.id,
            date_naissance=personne.date_naissance,
            date_mort=personne.date_mort,
            prenoms=prenoms,
            noms=noms,
            parents=parents,
            enfants=enfants,
        ))
    return resultat


@app.get("/personnes/{id_personne}", response_model=schemas.PersonneRead)
def lire_personne(id_personne: int, session: Session = Depends(get_session)):
    personne = getPersonne(session, id_personne)

    prenoms = session.exec(select(Prenom).where(Prenom.id_personne == personne.id)).all()
    noms = session.exec(select(Nom).where(Nom.id_personne == personne.id)).all()
    parents = session.exec(select(LienParente).where(LienParente.id_enfant == personne.id)).all()
    enfants = session.exec(select(LienParente).where(LienParente.id_parent == personne.id)).all()

    return schemas.PersonneRead(
        id=personne.id,
        date_naissance=personne.date_naissance,
        date_mort=personne.date_mort,
        prenoms=prenoms,
        noms=noms,
        parents=parents,
        enfants=enfants,
    )


@app.post("/personnes/", response_model=List[schemas.PersonneRead], status_code=201)
def creer_personne(donnees: List[schemas.PersonneCreate], session: Session = Depends(get_session)):
    personnes = []
    for d in donnees:
        contraintes.verifier_dates(d.date_naissance, d.date_mort)
        personne = Personne(date_naissance=d.date_naissance, date_mort=d.date_mort)
        session.add(personne)
        session.flush()
        for p in d.prenoms:
            session.add(Prenom(id_personne=personne.id, prenom=p))
        for n in d.noms:
            session.add(Nom(id_personne=personne.id, nom=n))
        for parent in d.parents:
            getPersonne(session, parent.id_parent)
            contraintes.verifier_parents_biologique(session, personne.id, parent.type_lien)
            contraintes.verifier_cycle_genealogique(session, personne.id, parent.id_parent)
            session.add(LienParente(id_enfant=personne.id, id_parent=parent.id_parent, type_lien=parent.type_lien))
        personnes.append(personne)
    verifierContrainteBdd(session)
    resultat = []
    for personne in personnes:
        session.refresh(personne)
        resultat.append(schemas.PersonneRead(
            id=personne.id,
            date_naissance=personne.date_naissance,
            date_mort=personne.date_mort,
            prenoms=session.exec(select(Prenom).where(Prenom.id_personne == personne.id)).all(),
            noms=session.exec(select(Nom).where(Nom.id_personne == personne.id)).all(),
            parents=session.exec(select(LienParente).where(LienParente.id_enfant == personne.id)).all(),
            enfants=session.exec(select(LienParente).where(LienParente.id_parent == personne.id)).all(),
        ))
    return resultat


@app.patch("/personnes/{id_personne}", response_model=schemas.PersonneRead)
def modifier_personne(id_personne: int, donnees: schemas.PersonneUpdate, session: Session = Depends(get_session)):
    personne = getPersonne(session, id_personne)

    nouvelle_naissance = donnees.date_naissance if donnees.date_naissance is not None else personne.date_naissance
    nouveau_mort = donnees.date_mort if donnees.date_mort is not None else personne.date_mort
    contraintes.verifier_dates(nouvelle_naissance, nouveau_mort)

    if donnees.date_naissance is not None:
        personne.date_naissance = donnees.date_naissance
    if donnees.date_mort is not None:
        personne.date_mort = donnees.date_mort

    if donnees.prenoms is not None:
        anciens_prenoms = session.exec(select(Prenom).where(Prenom.id_personne == id_personne)).all()
        for ancien in anciens_prenoms:
            session.delete(ancien)
        session.flush()
        for p in donnees.prenoms:
            session.add(Prenom(id_personne=id_personne, prenom=p))

    if donnees.noms is not None:
        anciens_noms = session.exec(select(Nom).where(Nom.id_personne == id_personne)).all()
        for ancien in anciens_noms:
            session.delete(ancien)
        session.flush()
        for n in donnees.noms:
            session.add(Nom(id_personne=id_personne, nom=n))

    session.add(personne)
    verifierContrainteBdd(session)
    session.refresh(personne)

    return schemas.PersonneRead(
        id=personne.id,
        date_naissance=personne.date_naissance,
        date_mort=personne.date_mort,
        prenoms=session.exec(select(Prenom).where(Prenom.id_personne == personne.id)).all(),
        noms=session.exec(select(Nom).where(Nom.id_personne == personne.id)).all(),
        parents=session.exec(select(LienParente).where(LienParente.id_enfant == personne.id)).all(),
        enfants=session.exec(select(LienParente).where(LienParente.id_parent == personne.id)).all(),
    )


@app.delete("/personnes/{id_personne}", status_code=204)
def supprimer_personne(id_personne: int, session: Session = Depends(get_session)):
    personne = getPersonne(session, id_personne)

    for lien in session.exec(select(LienParente).where(LienParente.id_parent == id_personne)).all():
        session.delete(lien)
    for lien in session.exec(select(LienParente).where(LienParente.id_enfant == id_personne)).all():
        session.delete(lien)
    for couple in session.exec(select(Couple).where(
        or_(Couple.id_personne_1 == id_personne, Couple.id_personne_2 == id_personne)
    )).all():
        session.delete(couple)

    session.flush()
    session.delete(personne)
    verifierContrainteBdd(session)


@app.post("/personnes/{id_personne}/prenoms", response_model=schemas.PersonneRead, status_code=201)
def ajouter_prenom(id_personne: int, donnees: schemas.PrenomCreate, session: Session = Depends(get_session)):
    personne = getPersonne(session, id_personne)
    session.add(Prenom(id_personne=id_personne, prenom=donnees.prenom))
    verifierContrainteBdd(session)
    session.refresh(personne)
    return schemas.PersonneRead(
        id=personne.id, date_naissance=personne.date_naissance, date_mort=personne.date_mort,
        prenoms=session.exec(select(Prenom).where(Prenom.id_personne == id_personne)).all(),
        noms=session.exec(select(Nom).where(Nom.id_personne == id_personne)).all(),
        parents=session.exec(select(LienParente).where(LienParente.id_enfant == id_personne)).all(),
        enfants=session.exec(select(LienParente).where(LienParente.id_parent == id_personne)).all(),
    )


@app.delete("/personnes/{id_personne}/prenoms/{prenom}", status_code=204)
def supprimer_prenom(id_personne: int, prenom: str, session: Session = Depends(get_session)):
    getPersonne(session, id_personne)
    entree = session.exec(select(Prenom).where(
        Prenom.id_personne == id_personne, Prenom.prenom == prenom
    )).first()
    if not entree:
        raise HTTPException(status_code=404, detail="Prénom introuvable.")
    session.delete(entree)
    verifierContrainteBdd(session)


@app.post("/personnes/{id_personne}/noms", response_model=schemas.PersonneRead, status_code=201)
def ajouter_nom(id_personne: int, donnees: schemas.NomCreate, session: Session = Depends(get_session)):
    personne = getPersonne(session, id_personne)
    session.add(Nom(id_personne=id_personne, nom=donnees.nom))
    verifierContrainteBdd(session)
    session.refresh(personne)
    return schemas.PersonneRead(
        id=personne.id, date_naissance=personne.date_naissance, date_mort=personne.date_mort,
        prenoms=session.exec(select(Prenom).where(Prenom.id_personne == id_personne)).all(),
        noms=session.exec(select(Nom).where(Nom.id_personne == id_personne)).all(),
        parents=session.exec(select(LienParente).where(LienParente.id_enfant == id_personne)).all(),
        enfants=session.exec(select(LienParente).where(LienParente.id_parent == id_personne)).all(),
    )


@app.delete("/personnes/{id_personne}/noms/{nom}", status_code=204)
def supprimer_nom(id_personne: int, nom: str, session: Session = Depends(get_session)):
    getPersonne(session, id_personne)
    entree = session.exec(select(Nom).where(
        Nom.id_personne == id_personne, Nom.nom == nom
    )).first()
    if not entree:
        raise HTTPException(status_code=404, detail="Nom introuvable.")
    session.delete(entree)
    verifierContrainteBdd(session)


@app.post("/personnes/{id_personne}/parents", response_model=List[schemas.LienParenteRead], status_code=201)
def ajouter_parent(id_personne: int, donnees: List[schemas.LienParenteCreate], session: Session = Depends(get_session)):
    getPersonne(session, id_personne)
    liens = []
    for d in donnees:
        getPersonne(session, d.id_parent)
        contraintes.verifier_parents_biologique(session, id_personne, d.type_lien)
        contraintes.verifier_cycle_genealogique(session, id_personne, d.id_parent)
        lien_existant = session.exec(select(LienParente).where(
            LienParente.id_enfant == id_personne,
            LienParente.id_parent == d.id_parent,
            LienParente.type_lien == d.type_lien,
        )).first()
        if lien_existant:
            raise HTTPException(status_code=409, detail="Ce lien de parenté existe déjà.")
        lien = LienParente(id_enfant=id_personne, id_parent=d.id_parent, type_lien=d.type_lien)
        session.add(lien)
        liens.append(lien)
    verifierContrainteBdd(session)
    for lien in liens:
        session.refresh(lien)
    return liens


@app.delete("/personnes/{id_personne}/parents/{id_parent}", status_code=204)
def supprimer_lien_parent(
    id_personne: int,
    id_parent: int,
    type_lien: TypeLien = TypeLien.BIOLOGIQUE,
    session: Session = Depends(get_session),
):
    lien = session.exec(select(LienParente).where(
        LienParente.id_enfant == id_personne,
        LienParente.id_parent == id_parent,
        LienParente.type_lien == type_lien,
    )).first()
    if not lien:
        raise HTTPException(status_code=404, detail="Lien de parenté introuvable.")
    session.delete(lien)
    verifierContrainteBdd(session)


@app.get("/couples/", response_model=List[schemas.CoupleRead])
def lister_couples(session: Session = Depends(get_session)):
    return session.exec(select(Couple)).all()


@app.get("/couples/{id_couple}", response_model=schemas.CoupleRead)
def lire_couple(id_couple: int, session: Session = Depends(get_session)):
    couple = session.get(Couple, id_couple)
    if not couple:
        raise HTTPException(status_code=404, detail=f"Couple {id_couple} introuvable.")
    return couple


@app.post("/couples/", response_model=schemas.CoupleRead, status_code=201)
def creer_couple(donnees: schemas.CoupleCreate, session: Session = Depends(get_session)):
    if donnees.id_personne_1 == donnees.id_personne_2:
        raise HTTPException(status_code=422, detail="Une personne ne peut pas être en couple avec elle-même.")

    getPersonne(session, donnees.id_personne_1)
    getPersonne(session, donnees.id_personne_2)

    p1 = min(donnees.id_personne_1, donnees.id_personne_2)
    p2 = max(donnees.id_personne_1, donnees.id_personne_2)

    couple_existant = session.exec(select(Couple).where(
        Couple.id_personne_1 == p1,
        Couple.id_personne_2 == p2
    )).first()
    if couple_existant:
        raise HTTPException(status_code=409, detail="Ce couple existe déjà.")

    couple = Couple(id_personne_1=p1, id_personne_2=p2)
    session.add(couple)
    verifierContrainteBdd(session)
    session.refresh(couple)
    return couple


@app.delete("/couples/{id_couple}", status_code=204)
def supprimer_couple(id_couple: int, session: Session = Depends(get_session)):
    couple = session.get(Couple, id_couple)
    if not couple:
        raise HTTPException(status_code=404, detail=f"Couple {id_couple} introuvable.")
    session.delete(couple)
    verifierContrainteBdd(session)