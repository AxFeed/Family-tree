# Contraintes métier

## Dates

- La date de décès ne peut pas être antérieure à la date de naissance.

---

## Liens de parenté

### Nombre de parents biologiques
- Une personne ne peut pas avoir plus de **2 parents biologiques**.

### Cycle généalogique
- Il est interdit de créer un cycle dans l'arbre généalogique (ex : A est parent de B, et B est parent de A).

### Doublon de lien
- Un même lien `(id_enfant, id_parent, type_lien)` ne peut pas être créé deux fois.

### Types de lien disponibles
| Valeur | Description |
|---|---|
| `BIOLOGIQUE` | Lien de filiation biologique (défaut) |
| `ADOPTIF` | Lien de filiation adoptive |
| `BEAU_PARENT` | Lien avec un beau-parent |

---

## Suppression d'une personne

- La suppression d'une personne entraîne la suppression en cascade de :
  - tous les liens de parenté où elle est **parent** (`id_parent`)
  - tous les couples auxquels elle appartient
- Les liens où elle est **enfant** (`id_enfant`) sont supprimés automatiquement par la contrainte `ON DELETE CASCADE` de la base de données.

---

## Couples

- Une personne ne peut pas être en couple avec **elle-même**.
- Un même couple `(id_personne_1, id_personne_2)` ne peut pas être créé deux fois.
