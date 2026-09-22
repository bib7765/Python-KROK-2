"""Demonstrate all four functions of the asynchronous module."""

import asyncio
import sys

from translation_package import AUTHOR, NAME
from translation_package.google_async import CodeLang, LangDetect, LanguageList, TransLate


async def main() -> None:
    print(NAME, "— googletrans 4.0.2")
    print(AUTHOR)
    print("Python:", sys.version.split()[0])
    text = "Добрий день! Сьогодні ми вивчаємо модулі та пакети Python."
    print("Текст:", text)
    print("Переклад uk → en:", await TransLate(text, "ukrainian", "english"))
    print(await LangDetect(text))
    print("CodeLang('uk'):", await CodeLang("uk"))
    print("CodeLang('english'):", await CodeLang("english"))
    print("LanguageList('file'):", await LanguageList("file"))
    print("Таблиця мов: languages_google_async.txt")


if __name__ == "__main__":
    asyncio.run(main())
