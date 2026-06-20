from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
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


@dataclass(frozen=True)
class PublicDatasetTrainingResult:
    dataset_name: str
    train_rows: int
    validation_rows: int
    test_rows: int
    labels: list[str]
    baseline_test_accuracy: float
    baseline_test_macro_f1: float
    validation_accuracy: float
    validation_macro_f1: float
    test_accuracy: float
    test_macro_f1: float
    improvement_test_accuracy: float
    improvement_test_macro_f1: float
    learned_weight_shape: tuple[int, int]
    confusion_matrix: list[list[int]]
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


def train_on_public_dataset(
    dataset_path: str | Path,
    output_dir: str | Path | None = None,
) -> tuple[Pipeline, PublicDatasetTrainingResult]:
    rows = pd.read_csv(dataset_path, sep="\t")
    required_columns = {"split", "label", "text"}
    missing = required_columns - set(rows.columns)
    if missing:
        raise ValueError(f"public dataset missing columns: {sorted(missing)}")

    train_rows = rows[rows["split"] == "train"]
    validation_rows = rows[rows["split"] == "validation"]
    test_rows = rows[rows["split"] == "test"]
    if train_rows.empty or validation_rows.empty or test_rows.empty:
        raise ValueError("public dataset must include train, validation, and test rows")

    x_train = train_rows["text"].astype(str).tolist()
    y_train = train_rows["label"].astype(str).tolist()
    x_validation = validation_rows["text"].astype(str).tolist()
    y_validation = validation_rows["label"].astype(str).tolist()
    x_test = test_rows["text"].astype(str).tolist()
    y_test = test_rows["label"].astype(str).tolist()
    labels = sorted(set(y_train) | set(y_validation) | set(y_test))

    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(x_train, y_train)
    baseline_test_pred = baseline.predict(x_test)

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=2000)),
            ("classifier", LogisticRegression(max_iter=1000, random_state=13)),
        ]
    )
    model.fit(x_train, y_train)
    validation_pred = model.predict(x_validation)
    test_pred = model.predict(x_test)

    target_dir = Path(output_dir) if output_dir else Path("demo_outputs")
    target_dir.mkdir(parents=True, exist_ok=True)
    model_path = target_dir / "public_sms_classifier.joblib"
    joblib.dump(model, model_path)
    try:
        artifact_model_path = model_path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        artifact_model_path = model_path.name

    baseline_test_accuracy = float(accuracy_score(y_test, baseline_test_pred))
    baseline_test_macro_f1 = float(f1_score(y_test, baseline_test_pred, average="macro"))
    validation_accuracy = float(accuracy_score(y_validation, validation_pred))
    validation_macro_f1 = float(f1_score(y_validation, validation_pred, average="macro"))
    test_accuracy = float(accuracy_score(y_test, test_pred))
    test_macro_f1 = float(f1_score(y_test, test_pred, average="macro"))
    classifier = model.named_steps["classifier"]
    result = PublicDatasetTrainingResult(
        dataset_name="UCI SMS Spam Collection compact subset",
        train_rows=len(train_rows),
        validation_rows=len(validation_rows),
        test_rows=len(test_rows),
        labels=labels,
        baseline_test_accuracy=round(baseline_test_accuracy, 3),
        baseline_test_macro_f1=round(baseline_test_macro_f1, 3),
        validation_accuracy=round(validation_accuracy, 3),
        validation_macro_f1=round(validation_macro_f1, 3),
        test_accuracy=round(test_accuracy, 3),
        test_macro_f1=round(test_macro_f1, 3),
        improvement_test_accuracy=round(test_accuracy - baseline_test_accuracy, 3),
        improvement_test_macro_f1=round(test_macro_f1 - baseline_test_macro_f1, 3),
        learned_weight_shape=tuple(int(value) for value in classifier.coef_.shape),
        confusion_matrix=confusion_matrix(y_test, test_pred, labels=labels).tolist(),
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


def write_public_dataset_artifacts(
    dataset_path: str | Path,
    output_dir: str | Path,
) -> PublicDatasetTrainingResult:
    _model, result = train_on_public_dataset(dataset_path, output_dir)
    target = Path(output_dir)
    (target / "public_sms_metrics.json").write_text(
        json.dumps(asdict(result), indent=2) + "\n",
        encoding="utf-8",
    )
    confusion_payload = {"labels": result.labels, "matrix": result.confusion_matrix}
    (target / "public_sms_confusion_matrix.json").write_text(
        json.dumps(confusion_payload, indent=2) + "\n",
        encoding="utf-8",
    )
    (target / "public_sms_report.md").write_text(_public_dataset_report(result), encoding="utf-8")
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


def _public_dataset_report(result: PublicDatasetTrainingResult) -> str:
    return (
        "\n".join(
            [
                "# Public Dataset Training Report",
                "",
                f"Dataset: {result.dataset_name}",
                "",
                "## Split",
                "",
                f"- Train rows: {result.train_rows}",
                f"- Validation rows: {result.validation_rows}",
                f"- Test rows: {result.test_rows}",
                f"- Labels: {', '.join(result.labels)}",
                "",
                "## Metrics",
                "",
                f"- Baseline test accuracy: {result.baseline_test_accuracy}",
                f"- Trained validation accuracy: {result.validation_accuracy}",
                f"- Trained test accuracy: {result.test_accuracy}",
                f"- Baseline test macro-F1: {result.baseline_test_macro_f1}",
                f"- Trained validation macro-F1: {result.validation_macro_f1}",
                f"- Trained test macro-F1: {result.test_macro_f1}",
                f"- Learned coefficient shape: {result.learned_weight_shape}",
                "",
                "## Confusion Matrix",
                "",
                f"Labels: {', '.join(result.labels)}",
                "",
                "```json",
                json.dumps(result.confusion_matrix),
                "```",
                "",
                "The public-dataset path uses a locally bundled UCI SMS Spam subset. It is a stronger signal than the tiny synthetic demo, while still staying small enough for offline CI.",
            ]
        )
        + "\n"
    )
