In the University of Tokyo's GCI World 2026 program, the module 7 competition revisits the Home
Credit problem: given a client's profile, estimate the probability that they won't repay their loan.
The training set has **171,202 clients** described by **32 features**, plus a `TARGET` column that is
1 when the client defaulted.

Before training anything, I looked at that column. That's where everything is decided.

## 13,821 defaults out of 171,202 clients

```python
import pandas as pd

train = pd.read_csv("input/train.csv")
train["TARGET"].value_counts(normalize=True)
# 0    0.9193
# 1    0.0807
```

Only **8.1%** of clients default. The other 91.9% repay. The dataset is heavily **imbalanced**, and
that completely changes how a model should be judged.

## The model that does nothing

Take the dumbest possible model: it answers "repays" for everyone, without even looking at the data.
scikit-learn ships one, the `DummyClassifier`, precisely to serve as a baseline.

```python
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, roc_auc_score

X = train.drop(columns=["SK_ID_CURR", "TARGET"])
y = train["TARGET"]

naive = DummyClassifier(strategy="most_frequent").fit(X, y)
accuracy_score(y, naive.predict(X))          # 0.919
roc_auc_score(y, naive.predict_proba(X)[:, 1])  # 0.5
```

**92% accuracy** while learning nothing. This model doesn't catch a single defaulter, which are
exactly the clients a bank needs to find. Judged on accuracy, it would have looked excellent.

That's the main lesson: **a metric only means something compared to a baseline**. Before celebrating
a score, you need to know what a model that does nothing gets.

## What ROC AUC measures

The competition is scored on **ROC AUC**, for a good reason. Instead of looking at yes/no
predictions, it looks at the **order** in which the model ranks clients by risk.

The simplest interpretation: pick at random one client who defaulted and one who repaid. ROC AUC is
the probability that the model gives the first one a higher risk score.

- **0.5**: the model ranks at random. That's the naive model's score above.
- **1.0**: every defaulter is ranked above every good payer.

For a bank, that's the right question. It doesn't need a binary verdict, it needs to know **which
files to review first**. And ROC AUC isn't fooled by the imbalance: answering "repays" for everyone
gives 0.5, not 0.92.

## How it changed my approach

This shaped the rest of my work on the competition:

1. **A baseline first.** The naive model sets the floor: 0.5 ROC AUC. Any model has to do clearly
   better to be worth looking at.
2. **Stratified cross-validation.** With 8% positives, a random split can produce folds with more
   or fewer defaults. `StratifiedKFold` keeps the same proportion in every fold, so the scores stay
   comparable.
3. **Probabilities, not classes.** Evaluate with `predict_proba`, not `predict`: ROC AUC needs a
   continuous risk score to rank clients.

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
cross_val_score(model, X_prepared, y, cv=cv, scoring="roc_auc")
```

## Takeaway

On an imbalanced dataset, accuracy rewards the model that ignores the rare class. Before choosing an
algorithm, choose **how you'll judge it**, and measure what a do-nothing model scores. That's what
separates an impressive number from a genuinely useful model.

*The competition is still running: I'll add my final score and the features that mattered most once
the leaderboard is published.*
