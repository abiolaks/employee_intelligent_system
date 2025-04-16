import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import joblib


class FeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_ = X.copy()
        X_["hire_date"] = pd.to_datetime(X_["hire_date"], errors="coerce")
        X_["last_promotion_date"] = pd.to_datetime(
            X_["last_promotion_date"], errors="coerce"
        )
        X_["years_since_last_promotion"] = (
            pd.to_datetime("today") - X_["last_promotion_date"]
        ).dt.days / 365
        X_["employment_age"] = (pd.to_datetime("today") - X_["hire_date"]).dt.days / 365
        return X_.drop(columns=["hire_date", "last_promotion_date"])


class PreprocessingPipeline:
    def __init__(self):
        self.categorical_features = ["department"]
        self.numerical_features = [
            "salary",
            "tenure",
            "engagement_score",
            "working_hours_per_month",
            "kpi_score",
            "work_life_balance_score",
            "overtime_hours",
            "job_satisfaction",
            "number_of_projects",
            "distance_from_home",
            "trainings_and_certifications",
            "years_since_last_promotion",
            "employment_age",
        ]
        self.pipeline = self._build_pipeline()

    def _build_pipeline(self):
        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]
        )

        numerical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )

        preprocessor = Pipeline(
            steps=[
                ("feature_engineering", FeatureEngineer()),
                (
                    "transform",
                    ColumnTransformer(
                        transformers=[
                            ("num", numerical_pipeline, self.numerical_features),
                            ("cat", categorical_pipeline, self.categorical_features),
                        ]
                    ),
                ),
            ]
        )

        return preprocessor

    def fit(self, X):
        self.pipeline.fit(X)

    def transform(self, X):
        return self.pipeline.transform(X)

    def fit_transform(self, X):
        return self.pipeline.fit_transform(X)

    def save(self, path):
        joblib.dump(self.pipeline, path)

    def load(self, path):
        self.pipeline = joblib.load(path)
