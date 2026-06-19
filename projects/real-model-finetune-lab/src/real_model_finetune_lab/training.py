from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline

from .dataset import TextExample, load_examples


@dataclass(frozen=True)
class TrainingResult:
    train_rows: int
    eval_rows: int
    labels: list[str]
    baseline_accuracy: float
    baseline_macro_f1: float
    trained_accuracy: float
    trained_macro_f1: float
    improvement_accuracy: float
    improvement_macro_f1: float
    learned_weight_shape: tuple[int, int]
    model_path: str


def split_examples(examples: list[TextExample]) -> tuple[list[TextExample], list[TextExample]]:
    train = [example for example in examples if example.split == "train"]
    eval_rows = [example for example in examples if example.split == "eval"]
    if not train or not eval_rows:
        raise ValueError("examples must include train and eval splits")
    return train, eval_rows


def train_text_classifier(
    examples_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> tuple[Pipeline, TrainingResult]:
    examples = load_examples(examples_path)
    train_rows, eval_rows = split_examples(examples)
    x_train = [row.text for row in train_rows]
    y_train = [row.label for row in train_rows]
    x_eval = [row.text for row in eval_rows]
    y_eval = [row.label for row in eval_rows]

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(x_train, y_train)
    baseline_pred = baseline.predict(x_eval)

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            (
                "classifier",
                LogisticRegression(max_iter=1000, random_state=7),
            ),
        ]
    )
    model.fit(x_train, y_train)
    trained_pred = model.predict(x_eval)

    classifier = model.named_steps["classifier"]
    labels = sorted(set(y_train) | set(y_eval))
    target_dir = Path(output_dir) if output_dir else Path("demo_outputs")
    target_dir.mkdir(parents=True, exist_ok=True)
    model_path = target_dir / "text_classifier.joblib"
    joblib.dump(model, model_path)
    try:
        artifact_model_path = model_path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        artifact_model_path = model_path.name

    baseline_accuracy = float(accuracy_score(y_eval, baseline_pred))
    baseline_macro_f1 = float(f1_score(y_eval, baseline_pred, average="macro"))
    trained_accuracy = float(accuracy_score(y_eval, trained_pred))
    trained_macro_f1 = float(f1_score(y_eval, trained_pred, average="macro"))
    result = TrainingResult(
        train_rows=len(train_rows),
        eval_rows=len(eval_rows),
        labels=labels,
        baseline_accuracy=round(baseline_accuracy, 3),
        baseline_macro_f1=round(baseline_macro_f1, 3),
        trained_accuracy=round(trained_accuracy, 3),
        trained_macro_f1=round(trained_macro_f1, 3),
        improvement_accuracy=round(trained_accuracy - baseline_accuracy, 3),
        improvement_macro_f1=round(trained_macro_f1 - baseline_macro_f1, 3),
        learned_weight_shape=tuple(int(value) for value in classifier.coef_.shape),
        model_path=artifact_model_path,
    )
    return model, result


def predict_label(model: Pipeline, text: str) -> dict[str, Any]:
    label = str(model.predict([text])[0])
    probabilities = model.predict_proba([text])[0]
    classes = [str(value) for value in model.classes_]
    return {
        "label": label,
        "probabilities": {
            class_name: round(float(probability), 3)
            for class_name, probability in zip(classes, probabilities, strict=True)
        },
    }


def write_training_artifacts(
    examples_path: str | Path,
    output_dir: str | Path,
) -> TrainingResult:
    model, result = train_text_classifier(examples_path, output_dir)
    target = Path(output_dir)
    metrics_path = target / "metrics.json"
    metrics_path.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
    sample_prediction = predict_label(
        model,
        "validate schema and log model prediction drift for monitoring",
    )
    (target / "sample_prediction.json").write_text(
        json.dumps(sample_prediction, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "model_card.md").write_text(_model_card(result), encoding="utf-8")
    return result


def _model_card(result: TrainingResult) -> str:
    return (
        "\n".join(
            [
                "# Real Model Fine-Tune Lab Model Card",
                "",
                "Small scikit-learn text classifier trained on synthetic portfolio task text.",
                "",
                "## Metrics",
                "",
                f"- Train rows: {result.train_rows}",
                f"- Eval rows: {result.eval_rows}",
                f"- Labels: {', '.join(result.labels)}",
                f"- Baseline accuracy: {result.baseline_accuracy}",
                f"- Trained accuracy: {result.trained_accuracy}",
                f"- Baseline macro-F1: {result.baseline_macro_f1}",
                f"- Trained macro-F1: {result.trained_macro_f1}",
                f"- Learned coefficient shape: {result.learned_weight_shape}",
                "",
                "## Scope",
                "",
                "This is real fitted model work, but the dataset is synthetic and small. It should be read as evidence of an end-to-end training/evaluation workflow, not production NLP quality.",
            ]
        )
        + "\n"
    )
