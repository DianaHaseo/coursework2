from src.aeroplane import Aeroplane


def filter_aeroplanes_by_country(
    aeroplanes: list[Aeroplane],
    countries: list[str],
) -> list[Aeroplane]:
    """Получить самолёты по стране регистрации."""

    if not isinstance(aeroplanes, list):
        raise TypeError(
            "Список самолётов должен быть представлен списком."
        )

    if not isinstance(countries, list):
        raise TypeError(
            "Страны должны быть представлены списком."
        )

    normalized_countries = {
        country.strip().lower()
        for country in countries
        if isinstance(country, str) and country.strip()
    }

    if not normalized_countries:
        raise ValueError(
            "Необходимо указать хотя бы одну страну."
        )

    return [
        aeroplane
        for aeroplane in aeroplanes
        if aeroplane.origin_country.lower()
        in normalized_countries
    ]


def sort_aeroplanes_by_altitude(
    aeroplanes: list[Aeroplane],
) -> list[Aeroplane]:
    """Отсортировать самолёты по высоте по убыванию."""

    if not isinstance(aeroplanes, list):
        raise TypeError(
            "Самолёты должны быть представлены списком."
        )

    return sorted(
        aeroplanes,
        key=lambda aeroplane: aeroplane.altitude,
        reverse=True,
    )


def get_top_aeroplanes(
    aeroplanes: list[Aeroplane],
    n: int,
) -> list[Aeroplane]:
    """Получить Top N самолётов по высоте."""

    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError(
            "N должно быть целым числом."
        )

    if n <= 0:
        raise ValueError(
            "N должно быть больше нуля."
        )

    sorted_aeroplanes = sort_aeroplanes_by_altitude(
        aeroplanes,
    )

    return sorted_aeroplanes[:n]


def print_aeroplanes(
    aeroplanes: list[Aeroplane],
) -> None:
    """Вывести самолёты в человекочитаемом виде."""

    if not aeroplanes:
        print("Самолёты не найдены.")
        return

    for number, aeroplane in enumerate(
        aeroplanes,
        start=1,
    ):
        print(
            f"{number}. {aeroplane}"
        )