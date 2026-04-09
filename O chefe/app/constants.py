DEFAULT_UNITS: tuple[str, ...] = (
    "ADMAV Sede",
    "ADMAV Freguesia",
    "ADMAV Colônia",
    "MAV Recreio",
    "ADMAV Campo Grande",
    "ADMAV Praça Seca",
)


def church_menu_text() -> str:
    lines = [
        "Paz do Senhor. Antes de continuar, informe com qual igreja você deseja falar:",
        "",
    ]
    lines.extend(f"{index}. {unit}" for index, unit in enumerate(DEFAULT_UNITS, start=1))
    lines.extend(
        [
            "",
            "Você pode responder com o número da opção ou com o nome da unidade.",
        ]
    )
    return "\n".join(lines)
