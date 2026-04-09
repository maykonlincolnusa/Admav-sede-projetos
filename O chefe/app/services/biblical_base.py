import re


_BOOKS = [
    "Genesis",
    "Exodo",
    "Levitico",
    "Numeros",
    "Deuteronomio",
    "Josue",
    "Juizes",
    "Rute",
    "Samuel",
    "Reis",
    "Cronicas",
    "Esdras",
    "Neemias",
    "Ester",
    "Jo",
    "Salmo",
    "Salmos",
    "Proverbios",
    "Eclesiastes",
    "Cantares",
    "Isaias",
    "Jeremias",
    "Lamentacoes",
    "Ezequiel",
    "Daniel",
    "Oseias",
    "Joel",
    "Amos",
    "Obadias",
    "Jonas",
    "Miqueias",
    "Naum",
    "Habacuque",
    "Sofonias",
    "Ageu",
    "Zacarias",
    "Malaquias",
    "Mateus",
    "Marcos",
    "Lucas",
    "Joao",
    "Atos",
    "Romanos",
    "Corintios",
    "Galatas",
    "Efesios",
    "Filipenses",
    "Colossenses",
    "Tessalonicenses",
    "Timoteo",
    "Tito",
    "Filemom",
    "Hebreus",
    "Tiago",
    "Pedro",
    "Judas",
    "Apocalipse",
]

_BOOKS_PATTERN = "|".join(sorted(_BOOKS, key=len, reverse=True))
_REFERENCE_REGEX = re.compile(
    rf"\b(?:[1-3]\s*)?(?:{_BOOKS_PATTERN})\s+\d{{1,3}}:\d{{1,3}}(?:-\d{{1,3}})?\b",
    re.IGNORECASE,
)


def has_biblical_reference(text: str) -> bool:
    if not text:
        return False
    return bool(_REFERENCE_REGEX.search(text))


def ensure_biblical_base(text: str, base_reference: str = "Hebreus 10:24-25") -> str:
    if not text:
        return text
    if has_biblical_reference(text):
        return text
    return f"{text}\nBase biblica: {base_reference}."
