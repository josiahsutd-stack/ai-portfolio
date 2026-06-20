from pathlib import Path

from real_model_finetune_lab import (
    default_examples,
    predict_label,
    split_examples,
    train_on_public_dataset,
    train_text_classifier,
    write_public_dataset_artifacts,
    write_training_artifacts,
)


def test_real_model_training_improves_over_baseline(tmp_path: Path) -> None:
    model, result = train_text_classifier(output_dir=tmp_path)

    assert result.train_rows > result.eval_rows
    assert result.trained_accuracy > result.baseline_accuracy
    assert result.trained_macro_f1 > result.baseline_macro_f1
    assert result.learned_weight_shape[0] == len(result.labels)
    assert result.learned_weight_shape[1] > 0
    assert (tmp_path / "text_classifier.joblib").exists()

    prediction = predict_label(model, "retrieve source chunks and cite the matched clause")
    assert prediction["label"] in result.labels
    assert "probabilities" in prediction


def test_real_model_dataset_has_fixed_train_eval_splits() -> None:
    train_rows, eval_rows = split_examples(default_examples())

    assert {row.split for row in train_rows} == {"train"}
    assert {row.split for row in eval_rows} == {"eval"}
    assert {row.label for row in train_rows} == {"rag", "agent", "mlops"}
    assert {row.label for row in eval_rows} == {"rag", "agent", "mlops"}


def test_real_model_artifacts_are_written(tmp_path: Path) -> None:
    result = write_training_artifacts(
        "projects/real-model-finetune-lab/sample_data/training_examples.json",
        tmp_path,
    )

    assert result.trained_accuracy > result.baseline_accuracy
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "sample_prediction.json").exists()
    assert (tmp_path / "model_card.md").exists()
    assert (tmp_path / "text_classifier.joblib").exists()


def test_public_dataset_training_uses_held_out_test_set(tmp_path: Path) -> None:
    dataset_path = Path("projects/real-model-finetune-lab/sample_data/uci_sms_subset.tsv")
    model, result = train_on_public_dataset(dataset_path, tmp_path)

    assert result.train_rows == 160
    assert result.validation_rows == 40
    assert result.test_rows == 40
    assert result.labels == ["ham", "spam"]
    assert result.test_accuracy > result.baseline_test_accuracy
    assert result.test_macro_f1 > result.baseline_test_macro_f1
    assert result.learned_weight_shape[1] > 0
    assert len(result.confusion_matrix) == 2
    assert (tmp_path / "public_sms_classifier.joblib").exists()

    prediction = predict_label(model, "free prize claim now")
    assert prediction["label"] in result.labels


def test_public_dataset_artifacts_are_written(tmp_path: Path) -> None:
    dataset_path = Path("projects/real-model-finetune-lab/sample_data/uci_sms_subset.tsv")
    result = write_public_dataset_artifacts(dataset_path, tmp_path)

    assert result.test_accuracy > result.baseline_test_accuracy
    assert (tmp_path / "public_sms_metrics.json").exists()
    assert (tmp_path / "public_sms_confusion_matrix.json").exists()
    assert (tmp_path / "public_sms_report.md").exists()
    assert (tmp_path / "public_sms_classifier.joblib").exists()
