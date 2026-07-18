# Building Energy Regression Evaluation

Fixed-split evaluation on the bundled synthetic dataset. These results do not measure real building performance or simulation accuracy.

## Protocol

- Rows: 180 synthetic records
- Split: 135 train / 45 holdout
- Split seed: 13
- Baseline: predict the training-target mean for every holdout row

## Results

| System | MAE (kWh/m2/year) | R2 |
| --- | ---: | ---: |
| Random forest | 30.29 | 0.579 |
| Training-mean baseline | 42.50 | -0.004 |

The random forest reduces MAE by 0.287 relative to this baseline on the fixed synthetic holdout.

## One Holdout Example

- Source row index: 174
- Actual synthetic target: 263.37 kWh/m2/year
- Prediction: 331.07 kWh/m2/year
- Absolute error: 67.70 kWh/m2/year

## Interpretation Boundary

- The target is generated from hand-authored relationships plus random noise.
- One fixed split is regression evidence, not a robust estimate of real-world generalization.
- No measured utility data, weather files, calibrated simulation, uncertainty intervals, or external validation are included.
- The values must not be used for design, compliance, investment, or engineering decisions.
