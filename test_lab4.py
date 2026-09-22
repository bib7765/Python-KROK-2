"""Offline checks for the translation package and file processing."""

import asyncio
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import filetr
from translation_package import ERROR, code_or_name, language_code, save_table
from translation_package import google_async, google_legacy, deep_translation


class TranslationTests(unittest.TestCase):
    def test_language_lookup(self):
        languages = {"uk": "ukrainian", "en": "english"}
        self.assertEqual(code_or_name("UK", languages), "ukrainian")
        self.assertEqual(language_code(" English ", languages), "en")
        self.assertEqual(language_code("auto", languages, True), "auto")
        with self.assertRaises(ValueError):
            language_code("unknown", languages)

    def test_version_guard_before_import(self):
        with patch.object(google_legacy.sys, "version_info", (3, 14)):
            for result in (
                google_legacy.TransLate("hello"),
                google_legacy.LangDetect("hello"),
                google_legacy.CodeLang("en"),
                google_legacy.LanguageList(),
            ):
                self.assertTrue(result.startswith(ERROR))
                self.assertIn("3.13", result)

    def test_empty_text_and_invalid_mode(self):
        self.assertTrue(asyncio.run(google_async.TransLate(" ")).startswith(ERROR))
        self.assertTrue(asyncio.run(google_async.LangDetect("hello", "bad")).startswith(ERROR))
        self.assertTrue(deep_translation.TransLate("").startswith(ERROR))

    def test_sentences_keep_punctuation(self):
        self.assertEqual(filetr.split_sentences("Перше! Друге? Третє. Кінець"),
                         ["Перше!", "Друге?", "Третє.", "Кінець"])
        self.assertEqual(filetr.split_sentences("   "), [])

    def test_config_rejects_invalid_counts(self):
        config = {"filename": "text.txt", "language": "en", "module": "google_async",
                  "output": "screen", "sentences": 0}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            for count in (0, -1, True, 1.5):
                config["sentences"] = count
                path.write_text(json.dumps(config))
                with self.assertRaises(ValueError):
                    filetr.read_config(path)

    def test_table_has_no_translation_column_without_text(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(save_table([["Код", "Мова"], ["uk", "ukrainian"]],
                                        "screen", "unused.txt"), "Ok")
        self.assertNotIn("Переклад", stream.getvalue())

    def test_async_table_with_translation(self):
        async def translate(text, source, target):
            return "Hello"
        with patch.object(google_async, "LANGUAGES", {"en": "english"}), \
             patch.object(google_async, "TransLate", translate):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                result = asyncio.run(google_async.LanguageList("screen", "Привіт"))
            self.assertEqual(result, "Ok")
            self.assertIn("Переклад", stream.getvalue())
            self.assertIn("Hello", stream.getvalue())

    def test_file_translation_count_and_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "text.txt").write_text("Перше. Друге! Третє?", encoding="utf-8")
            config = {"filename": "text.txt", "language": "english", "module": "google_async",
                      "output": "file", "sentences": 2}
            (root / "config.json").write_text(json.dumps(config))
            async def translate(text, source, target):
                self.assertEqual(text, "Перше. Друге!")
                self.assertEqual(target, "en")
                return "First. Second!"
            async def detect(text, mode):
                return "uk"
            with patch.object(filetr, "ROOT", root), \
                 patch.object(google_async, "TransLate", translate), \
                 patch.object(google_async, "LangDetect", detect), \
                 contextlib.redirect_stdout(io.StringIO()):
                asyncio.run(filetr.translate_file(root / "config.json"))
            self.assertEqual((root / "text_en.txt").read_text(), "First. Second!\n")


if __name__ == "__main__":
    unittest.main()
