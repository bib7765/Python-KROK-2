"""Demonstrate deep-translator and langdetect."""

import sys

from translation_package import AUTHOR, NAME
from translation_package.deep_translation import CodeLang, LangDetect, LanguageList, TransLate


def main() -> None:
    print(NAME, "— deep-translator")
    print(AUTHOR)
    print("Python:", sys.version.split()[0])
    text = "Добрий день! Сьогодні ми вивчаємо модулі та пакети Python."
    print("Текст:", text)
    print("Переклад uk → en:", TransLate(text, "ukrainian", "english"))
    print(LangDetect(text))
    print("CodeLang('uk'):", CodeLang("uk"))
    print("CodeLang('english'):", CodeLang("english"))
    print("LanguageList('file'):", LanguageList("file"))
    print("Таблиця мов: languages_deep_translation.txt")


if __name__ == "__main__":
    main()
