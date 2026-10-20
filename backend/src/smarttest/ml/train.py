"""Model training, GroupKFold cross-validation, and probability calibration."""

from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import GroupKFold
from sklearn.metrics import average_precision_score, roc_auc_score
import joblib

from smarttest.config import SEED
from smarttest.features.builder import FEATURE_NAMES


def train_and_select_best_model(
    df_train: pd.DataFrame,
) -> Tuple[Any, str, Dict[str, Any]]:
    """Trains candidate classifiers with GroupKFold CV, picks highest PR-AUC, and calibrates."""
    X = df_train[FEATURE_NAMES].values
    y = df_train["detected"].values
    groups = df_train["mutant_id"].values

    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=SEED,
                ),
            ),
        ]),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight="balanced_subsample",
            random_state=SEED,
            n_jobs=-1,
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            class_weight="balanced",
            max_iter=100,
            random_state=SEED,
        ),
    }

    gkf = GroupKFold(n_splits=5)
    model_cv_scores: Dict[str, float] = {}

    for name, model in models.items():
        pr_aucs: List[float] = []
        for train_idx, val_idx in gkf.split(X, y, groups=groups):
            X_tr, y_tr = X[train_idx], y[train_idx]
            X_val, y_val = X[val_idx], y[val_idx]

            # Fit fold model
            model.fit(X_tr, y_tr)
            y_pred_proba = model.predict_proba(X_val)[:, 1]

            score = average_precision_score(y_val, y_pred_proba)
            pr_aucs.append(score)

        mean_pr_auc = float(np.mean(pr_aucs))
        model_cv_scores[name] = mean_pr_auc

    # Select best performing model
    best_name = max(model_cv_scores, key=model_cv_scores.get)
    best_estimator = models[best_name]

    # Train and calibrate final probability estimator on all training data
    # Use precomputed GroupKFold splits inside CalibratedClassifierCV
    cv_splits = list(gkf.split(X, y, groups=groups))
    calibrated = CalibratedClassifierCV(
        estimator=best_estimator,
        method="sigmoid",
        cv=cv_splits,
    )
    calibrated.fit(X, y)

    bundle = {
        "model": calibrated,
        "feature_names": FEATURE_NAMES,
        "selected_model": best_name,
        "cv_pr_aucs": model_cv_scores,
    }

    return bundle, best_name, model_cv_scores
