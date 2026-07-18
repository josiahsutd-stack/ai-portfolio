from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

from real_model_finetune_lab.public_subset import (  # noqa: E402
    build_subset,
    download_source_archive,
    load_source_archive,
    validate_checked_in_subset,
    write_subset,
)

DEFAULT_ARCHIVE = REPO_ROOT / ".artifacts" / "uci-sms-source.zip"
TSV_PATH = PROJECT_ROOT / "sample_data" / "uci_sms_subset.tsv"
MANIFEST_PATH = PROJECT_ROOT / "sample_data" / "uci_sms_subset_manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build or verify the deterministic UCI SMS subset."
    )
    parser.add_argument("--check", action="store_true", help="Verify checked-in provenance only.")
    parser.add_argument("--source-archive", type=Path, default=DEFAULT_ARCHIVE)
    args = parser.parse_args()

    if args.check:
        issues = validate_checked_in_subset(TSV_PATH, MANIFEST_PATH)
        if issues:
            print("Public SMS subset provenance check failed:")
            for issue in issues:
                print(f"- {issue}")
            raise SystemExit(1)
        print("Public SMS subset provenance check passed for 240 source-traceable rows.")
        return

    archive = args.source_archive
    if not archive.exists():
        print(f"Downloading official UCI archive to {archive}")
        download_source_archive(archive)
    rows = build_subset(load_source_archive(archive))
    write_subset(rows, TSV_PATH, MANIFEST_PATH)
    print(f"Wrote {len(rows)} deterministic rows to {TSV_PATH.relative_to(REPO_ROOT)}")
    print(f"Wrote provenance manifest to {MANIFEST_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
