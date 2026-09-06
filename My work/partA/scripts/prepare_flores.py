#!/usr/bin/env python3
"""Prepare a small, line-aligned FLORES-200 tokenizer evaluation corpus.

The archive is the official public FLORES-200 release.  We use its complete
devtest split (1,012 professionally translated sentences per language) rather
than sampling rows, so every target language represents the same meaning in
the same order.  The script writes UTF-8 NFC text and a manifest with the
archive SHA-256 for auditability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import tempfile
import unicodedata
import urllib.request
from pathlib import Path


SOURCE_URL = "https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz"
LANGUAGES = ("eng_Latn", "hin_Deva", "kan_Knda", "tam_Taml")
EXPECTED_SENTENCES = 1012


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    """Download atomically enough for a repeatable, manually inspectable run."""
    with urllib.request.urlopen(url) as response, destination.open("wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def member_for_language(archive: tarfile.TarFile, language: str) -> tarfile.TarInfo:
    wanted = f"flores200_dataset/devtest/{language}.devtest"
    for member in archive.getmembers():
        if member.name.lstrip("./") == wanted:
            return member
    raise FileNotFoundError(f"Missing {wanted} in FLORES archive")


def extract_lines(archive: tarfile.TarFile, language: str) -> list[str]:
    member = member_for_language(archive, language)
    payload = archive.extractfile(member)
    if payload is None:
        raise ValueError(f"Cannot read {member.name}")
    # Sentence files are newline-delimited data. Boundary whitespace is a file
    # serialization artifact, not part of the translated sentence; preserve
    # all interior whitespace because it is actual corpus content.
    lines = [unicodedata.normalize("NFC", line.strip()) for line in payload.read().decode("utf-8").splitlines()]
    if len(lines) != EXPECTED_SENTENCES:
        raise ValueError(f"{language}: expected {EXPECTED_SENTENCES} lines, found {len(lines)}")
    if any(not line.strip() for line in lines):
        raise ValueError(f"{language}: corpus contains an empty sentence")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "flores200_devtest",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="Existing FLORES-200 tar.gz. Omit to download from the official source.",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.archive:
        archive_path = args.archive.resolve()
        if not archive_path.is_file():
            raise FileNotFoundError(archive_path)
        temporary = None
    else:
        temporary = tempfile.TemporaryDirectory(prefix="flores200-")
        archive_path = Path(temporary.name) / "flores200_dataset.tar.gz"
        print(f"Downloading {SOURCE_URL}")
        download(SOURCE_URL, archive_path)

    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            lengths: dict[str, int] = {}
            for language in LANGUAGES:
                lines = extract_lines(archive, language)
                (output_dir / f"{language}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
                lengths[language] = len(lines)

        manifest = {
            "source_name": "FLORES-200",
            "source_url": SOURCE_URL,
            "split": "devtest",
            "languages": list(LANGUAGES),
            "sentence_count_per_language": lengths,
            "alignment": "Line i is the translation of the same source sentence in every language.",
            "preprocessing": "UTF-8 decode, line-ending normalization, leading/trailing Unicode whitespace removal, NFC normalization; no lowercasing or interior-whitespace collapsing.",
            "license": "CC-BY-SA-4.0 (FLORES-200)",
            "citation": "NLLB Team et al. (2022), No Language Left Behind: Scaling Human-Centered Machine Translation.",
            "archive_sha256": sha256(archive_path),
        }
        (output_dir / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    finally:
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    main()
