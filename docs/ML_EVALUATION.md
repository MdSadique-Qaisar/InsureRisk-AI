# ML Evaluation Guide

The training notebooks contain the original EDA, cleaning, feature engineering, model training, tuning, error analysis, and artifact export workflow.

The enhanced versions add the missing portfolio-level evaluation components:

1. Regression metrics: MAE, RMSE, R².
2. Mean and median baselines.
3. Linear Regression, Ridge, Random Forest, and XGBoost comparison.
4. Train vs test performance.
5. 5-fold cross-validation.
6. Global XGBoost feature importance.
7. SHAP summary analysis.
8. Mean absolute SHAP importance.
9. Final selected-model metrics.

## Recommended interpretation

Use **MAE** as the easiest-to-explain average absolute premium error.

Use **RMSE** when larger errors should be penalized more strongly.

Use **R²** to describe explained variance, but do not use R² alone to select a model.

Compare train/test performance to detect overfitting.

Use cross-validation on the training set and keep the final test set untouched until final model assessment.

## Important preprocessing note

The original notebooks fit the MinMaxScaler before the train/test split. For a production-grade retraining pipeline, fit preprocessing on the training set only and transform validation/test data with that fitted transformer. This prevents preprocessing leakage.

The current deployed artifacts should therefore be treated as reproductions of the existing project workflow; a future retraining pass should correct this issue and regenerate the artifacts.
