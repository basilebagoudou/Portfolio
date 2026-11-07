Dans le programme GCI World 2026 de l'Université de Tokyo, la compétition du module 7 reprend le
problème de Home Credit : à partir du profil d'un client, estimer la probabilité qu'il ne rembourse
pas son crédit. Le jeu d'entraînement compte **171 202 clients** décrits par **32 variables**, et une
colonne `TARGET` qui vaut 1 quand le client a fait défaut.

Avant d'entraîner quoi que ce soit, j'ai regardé cette colonne. C'est là que tout se joue.

## 13 821 défauts sur 171 202 clients

```python
import pandas as pd

train = pd.read_csv("input/train.csv")
train["TARGET"].value_counts(normalize=True)
# 0    0.9193
# 1    0.0807
```

Seuls **8,1 %** des clients font défaut. Les 91,9 % restants remboursent. Le jeu de données est
fortement **déséquilibré**, et ça change complètement la façon de juger un modèle.

## Le modèle qui ne fait rien

Prenons le modèle le plus bête possible : il répond « rembourse » pour tout le monde, sans même
regarder les données. scikit-learn en fournit un, le `DummyClassifier`, justement pour servir de
point de comparaison.

```python
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

X = train.drop(columns=["SK_ID_CURR", "TARGET"])
y = train["TARGET"]

naif = DummyClassifier(strategy="most_frequent").fit(X, y)
accuracy_score(y, naif.predict(X))          # 0.919
roc_auc_score(y, naif.predict_proba(X)[:, 1])  # 0.5
```

**92 % d'accuracy**, sans avoir rien appris. Ce modèle ne repère aucun mauvais payeur, c'est-à-dire
exactement les clients qu'une banque a besoin d'identifier. Si je l'avais jugé à l'accuracy, il
aurait eu l'air excellent.

C'est la leçon principale : **une métrique n'a de sens que comparée à une référence**. Avant de se
féliciter d'un score, il faut savoir combien obtient un modèle qui ne fait rien.

## Ce que mesure la ROC AUC

La compétition est évaluée à la **ROC AUC**, et pour une bonne raison. Au lieu de regarder des
prédictions oui/non, elle regarde **l'ordre** dans lequel le modèle classe les clients selon leur
risque.

L'interprétation la plus simple : si l'on tire au hasard un client qui a fait défaut et un client qui
a remboursé, la ROC AUC est la probabilité que le modèle donne un score de risque plus élevé au
premier.

- **0,5** : le modèle classe au hasard. C'est le score du modèle naïf ci-dessus.
- **1,0** : tous les mauvais payeurs sont classés avant tous les bons.

Pour une banque, c'est la bonne question. Elle n'a pas besoin d'un verdict binaire, elle a besoin de
savoir **quels dossiers examiner en premier**. Et la ROC AUC ne se laisse pas tromper par le
déséquilibre : répondre « rembourse » à tout le monde donne 0,5, pas 0,92.

## Ce que ça change dans ma démarche

Ce constat a guidé la suite de mon travail sur la compétition :

1. **Une référence d'abord.** Le modèle naïf fixe le plancher : 0,5 de ROC AUC. Tout modèle doit
   faire nettement mieux pour mériter qu'on s'y intéresse.
2. **Une validation croisée stratifiée.** Avec 8 % de positifs, un découpage au hasard peut produire
   des plis plus ou moins riches en défauts. `StratifiedKFold` garde la même proportion dans chaque
   pli, et donc des scores comparables.
3. **Des probabilités, pas des classes.** On évalue avec `predict_proba`, pas avec `predict` : la ROC
   AUC a besoin d'un score de risque continu pour classer les clients.

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
cross_val_score(modele, X_prepare, y, cv=cv, scoring="roc_auc")
```

## À retenir

Sur un jeu de données déséquilibré, l'accuracy récompense le modèle qui ignore la classe rare. Avant
de choisir un algorithme, il faut choisir **comment on va le juger**, et mesurer ce qu'obtient un
modèle qui ne fait rien. C'est ce qui sépare un chiffre impressionnant d'un modèle réellement utile.

*La compétition est toujours en cours : j'ajouterai mon score final et les variables qui ont le plus
compté une fois le classement publié.*
