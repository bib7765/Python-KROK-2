"""Translate the first N sentences using a JSON configuration."""

import argparse
import asyncio
import importlib
import inspect
import json
import re
from pathlib import Path

from translation_package import AUTHOR, ERROR, ROOT, language_code

MODULES = {"google_async", "google_legacy", "deep_translation"}


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.findall(r"[^.!?]+(?:[.!?]+|$)", text) if part.strip()]


def read_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("конфігурація повинна бути JSON-об'єктом")
    for key in ("filename", "language", "module", "output", "sentences"):
        if key not in config:
            raise ValueError(f"у конфігурації відсутнє поле {key}")
    if config["module"] not in MODULES:
        raise ValueError("невідомий модуль перекладу")
    if config["output"] not in ("screen", "file"):
        raise ValueError("output має бути screen або file")
    if type(config["sentences"]) is not int or config["sentences"] < 1:
        raise ValueError("sentences має бути додатним цілим числом")
    for key in ("filename", "language"):
        if not isinstance(config[key], str) or not config[key].strip():
            raise ValueError(f"поле {key} має містити непорожній рядок")
    if Path(config["filename"]).name != config["filename"]:
        raise ValueError("текстовий файл має бути в кореневому каталозі проєкту")
    return config


async def call(function, *args) -> str:
    result = function(*args)
    if inspect.isawaitable(result):
        result = await result
    if result.startswith(ERROR):
        raise ValueError(result.removeprefix(ERROR))
    return result


async def translate_file(config_path: Path) -> None:
    config = read_config(config_path)
    module = importlib.import_module("translation_package." + config["module"])
    if config["module"] == "google_legacy":
        module.check_runtime()
        from googletrans import LANGUAGES
        languages = LANGUAGES
    else:
        languages = module.LANGUAGES
    target = language_code(config["language"], languages)
    path = ROOT / config["filename"]
    text = path.read_text(encoding="utf-8")
    sentences = split_sentences(text)
    if not sentences:
        raise ValueError("вхідний файл порожній")
    print(AUTHOR)
    print("Конфігурація:", config_path.name)
    print("Файл:", path.name)
    print("Розмір:", path.stat().st_size, "байтів")
    print("Символів:", len(text))
    print("Речень у файлі:", len(sentences))
    print("Мова тексту:", await call(module.LangDetect, text, "lang"))
    selected = " ".join(sentences[:config["sentences"]])
    print("Речень для перекладу:", min(len(sentences), config["sentences"]))
    print(f"Мова перекладу: {languages[target]} ({target})")
    print("Модуль:", config["module"])
    translated = await call(module.TransLate, selected, "auto", target)
    if config["output"] == "screen":
        print("Переклад:\n" + translated)
    else:
        output_path = path.with_name(f"{path.stem}_{target}{path.suffix}")
        output_path.write_text(translated + "\n", encoding="utf-8")
        print("Результат:", output_path.name)
        print("Ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", nargs="?", type=Path, default=ROOT / "config.json")
    args = parser.parse_args()
    try:
        asyncio.run(translate_file(args.config))
        return 0
    except (OSError, ValueError, ImportError, RuntimeError) as error:
        print(ERROR + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
