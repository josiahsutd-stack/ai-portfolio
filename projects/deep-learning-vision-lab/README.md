# Deep Learning Vision Lab

Computer-vision defect detection lab using synthetic image data, a fast local baseline, metrics, Streamlit demo, and FastAPI metrics endpoint.

## Problem

Vision systems need dataset generation, preprocessing, evaluation, and deployment surfaces before model complexity matters.

## Demo

```bash
streamlit run projects/deep-learning-vision-lab/app.py
```

## Features

- Synthetic defect dataset generator
- Scratch/crack/OK classes
- Fast baseline classifier
- Accuracy and macro-F1 metrics
- Example predictions
- FastAPI `/metrics` endpoint

## Tech Stack

Python, NumPy, scikit-learn metrics, FastAPI, Streamlit. PyTorch training can be added without changing the project shape.

## Architecture

```mermaid
flowchart LR
  A["Synthetic images"] --> B["Preprocessing"]
  B --> C["Vision model/baseline"]
  C --> D["Metrics"]
  C --> E["Demo/API"]
```

## Limitations

- Synthetic image data and simple baseline.
- No real manufacturing images or production inspection claims.

## How I Would Improve This In Production

- Add PyTorch CNN/U-Net training, confusion matrices, real defect data, and latency benchmarks.

## What This Proves To Employers

Deep learning workflow understanding, computer vision evaluation, data generation, and inference packaging.

## Engineering Notes

- The lab is shaped around the deep learning workflow: dataset manifest, preprocessing, metrics, model card, API, and demo.
- Synthetic data keeps the project lightweight while allowing the repository to show evaluation and packaging discipline.
- The baseline is deliberately simple so the model interface can be replaced by PyTorch training without restructuring the app.
- Production use would require real labeled images, CNN/ViT training, augmentation, calibration, latency profiling, and error analysis by defect type.

## Technical Review Discussion Points

- Reviewers can distinguish workflow competence from production inspection accuracy claims.
- The project supports discussion of collecting, labeling, splitting, and auditing a real vision dataset.
- The metrics path extends beyond accuracy to error analysis and model behavior.
- The model card documents assumptions, limitations, and failure modes.
- PyTorch training can slot into the existing architecture without changing the demo/API shape.

