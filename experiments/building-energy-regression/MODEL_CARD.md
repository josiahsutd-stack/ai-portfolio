# Model Card: Synthetic Building Energy Regressor

## Status

Local portfolio experiment. The fitted scikit-learn pipeline is real; all training and evaluation rows are synthetic.

## Intended Use

Demonstrate tabular preprocessing, regression, baseline comparison, local inference, and evidence generation. The output is suitable only for software review and experimentation.

## Data

[`generate_sample_data.py`](../../scripts/generate_sample_data.py) creates 180 rows from hand-authored relationships among floor area, occupancy, glazing, insulation, operating hours, climate category, and HVAC category, then adds random noise. The resulting CSV contains no measured, customer, employer, or real-project data.

## Model

A `ColumnTransformer` one-hot encodes categorical fields and standardizes numeric fields. A `RandomForestRegressor` uses 120 estimators, `min_samples_leaf=3`, and `random_state=9`.

## Evaluation

The fixed `random_state=13` split contains `135` training rows and `45` holdout rows. The random forest records MAE `30.29` and R2 `0.579`; the training-target-mean baseline records MAE `42.50` and R2 `-0.004`. The random forest's MAE reduction relative to that baseline is `0.287`.

The source of record is [`energy_eval_summary.json`](demo_outputs/energy_eval_summary.json). [`energy_eval_report.md`](demo_outputs/energy_eval_report.md) documents the protocol and one honestly reported holdout error.

## Interpretation

The comparison confirms that the pipeline learns some of the synthetic generator's relationships better than a mean predictor on this split. It does not establish performance on measured buildings or demonstrate calibrated simulation accuracy.

## Limitations And Prohibited Uses

- One synthetic split is too narrow for model selection or real-world generalization claims.
- No external validation, cross-validation, uncertainty, subgroup error analysis, or drift study is included.
- Generated targets simplify building physics and omit many causal variables.
- Do not use the output for design, compliance, investment, utility forecasting, sustainability reporting, or professional engineering decisions.
