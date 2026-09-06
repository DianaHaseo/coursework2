from pathlib import Path

from src.aeroplane import Aeroplane
from src.api import APIError, AeroplanesAPI
from src.file_saver import JSONSaver, StorageError
from src.utils import (
    filter_aeroplanes_by_country,
    get_top_aeroplanes,
    print_aeroplanes,
)


DATA_FILE = Path(__file__).parent / "data" / "aeroplanes.json"


def user_interaction() -> None:
    """Основная функция взаимодействия с пользователем."""

    api = AeroplanesAPI()
    saver = JSONSaver(DATA_FILE)

    print("=== Поиск самолётов ===")

    country = input(
        "Введите название страны: "
    ).strip()

    if not country:
        print("Название страны не может быть пустым.")
        return

    try:
        states = api.get_aeroplanes(country)
    except (APIError, ValueError) as error:
        print(f"Ошибка получения данных: {error}")
        return

    aeroplanes = Aeroplane.cast_to_object_list(states)

    if not aeroplanes:
        print(
            f"В воздушном пространстве страны "
            f"'{country}' самолёты не найдены."
        )
        return

    for aeroplane in aeroplanes:
        try:
            saver.add_aeroplane(aeroplane)
        except (StorageError, TypeError) as error:
            print(
                f"Ошибка сохранения {aeroplane.callsign}: "
                f"{error}"
            )

    print(
        f"\nПолучено самолётов: {len(aeroplanes)}"
    )

    while True:
        print(
            "\n=== Меню ===\n"
            "1. Показать Top N самолётов по высоте\n"
            "2. Найти самолёты по стране регистрации\n"
            "3. Показать все полученные самолёты\n"
            "0. Выход"
        )

        choice = input(
            "Выберите действие: "
        ).strip()

        if choice == "1":
            show_top_n(aeroplanes)

        elif choice == "2":
            show_by_country(aeroplanes)

        elif choice == "3":
            print_aeroplanes(aeroplanes)

        elif choice == "0":
            print("Работа программы завершена.")
            break

        else:
            print(
                "Некорректный пункт меню."
            )


def show_top_n(
    aeroplanes: list[Aeroplane],
) -> None:
    """Показать Top N самолётов."""

    try:
        n = int(
            input(
                "Введите количество самолётов N: "
            )
        )

        top_aeroplanes = get_top_aeroplanes(
            aeroplanes,
            n,
        )

    except (ValueError, TypeError) as error:
        print(f"Ошибка: {error}")
        return

    print(
        f"\nTop {len(top_aeroplanes)} самолётов "
        f"по высоте:"
    )

    print_aeroplanes(top_aeroplanes)


def show_by_country(
    aeroplanes: list[Aeroplane],
) -> None:
    """Показать самолёты по стране регистрации."""

    countries_input = input(
        "Введите страны регистрации через запятую: "
    )

    countries = [
        country.strip()
        for country in countries_input.split(",")
    ]

    try:
        filtered = filter_aeroplanes_by_country(
            aeroplanes,
            countries,
        )
    except (ValueError, TypeError) as error:
        print(f"Ошибка: {error}")
        return

    print(
        f"\nНайдено самолётов: {len(filtered)}"
    )

    print_aeroplanes(filtered)


if __name__ == "__main__":
    user_interaction()

