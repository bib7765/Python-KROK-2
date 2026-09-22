"""Demonstrate the legacy module and its Python version guard."""

import sys

from translation_package import AUTHOR, NAME
from translation_package.google_legacy import (
    CodeLang, LangDetect, LanguageList, TransLate, check_runtime,
)


def main() -> int:
    print(NAME, "— googletrans 3.1.0a0")
    print(AUTHOR)
    print("Python:", sys.version.split()[0])
    try:
        check_runtime()
    except (RuntimeError, ImportError) as error:
        print("Помилка:", error)
        return 1
    text = "Добрий день! Сьогодні ми вивчаємо модулі та пакети Python."
    print("Текст:", text)
    print("Переклад uk → en:", TransLate(text, "ukrainian", "english"))
    print(LangDetect(text))
    print("CodeLang('uk'):", CodeLang("uk"))
    print("CodeLang('english'):", CodeLang("english"))
    print("LanguageList('file'):", LanguageList("file"))
    print("Таблиця мов: languages_google_legacy.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
