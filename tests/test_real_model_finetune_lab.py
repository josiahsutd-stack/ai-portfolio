from pathlib import Path

from real_model_finetune_lab import (
    default_examples,
    predict_label,
    split_examples,
    train_text_classifier,
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
