import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.aeroplane import Aeroplane


class StorageError(Exception):
    """Ошибка при работе с хранилищем."""


class BaseSaver(ABC):
    """Абстрактный класс для хранения информации о самолётах."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить самолёт."""

    @abstractmethod
    def get_aeroplanes(
        self,
        criteria: dict[str, Any] | None = None,
    ) -> list[Aeroplane]:
        """Получить самолёты по критериям."""

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """Удалить самолёт."""


class JSONSaver(BaseSaver):
    """Хранилище самолётов в JSON-файле."""

    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():
            self._write_data([])

    def _read_data(self) -> list[dict[str, Any]]:
        """Прочитать данные из JSON."""

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except FileNotFoundError:
            return []

        except json.JSONDecodeError as error:
            raise StorageError(
                "JSON-файл содержит некорректные данные."
            ) from error

        except OSError as error:
            raise StorageError(
                f"Ошибка чтения файла: {error}"
            ) from error

        if not isinstance(data, list):
            raise StorageError(
                "JSON-файл должен содержать список."
            )

        return data

    def _write_data(
        self,
        data: list[dict[str, Any]],
    ) -> None:
        """Записать данные в JSON."""

        try:
            with self.file_path.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

        except OSError as error:
            raise StorageError(
                f"Ошибка записи файла: {error}"
            ) from error

    def add_aeroplane(
        self,
        aeroplane: Aeroplane,
    ) -> None:
        """Добавить самолёт в JSON."""

        if not isinstance(aeroplane, Aeroplane):
            raise TypeError(
                "Можно добавить только объект Aeroplane."
            )

        data = self._read_data()

        for item in data:
            if item.get("icao24") == aeroplane.icao24:
                return

        data.append(aeroplane.to_dict())

        self._write_data(data)

    def get_aeroplanes(
        self,
        criteria: dict[str, Any] | None = None,
    ) -> list[Aeroplane]:
        """Получить самолёты и применить критерии фильтрации."""

        data = self._read_data()

        aeroplanes = []

        for item in data:
            try:
                aeroplane = Aeroplane(
                    icao24=item["icao24"],
                    callsign=item["callsign"],
                    origin_country=item["origin_country"],
                    velocity=item["velocity"],
                    altitude=item["altitude"],
                    latitude=item.get("latitude"),
                    longitude=item.get("longitude"),
                )
            except (KeyError, TypeError, ValueError):
                continue

            aeroplanes.append(aeroplane)

        if criteria is None:
            return aeroplanes

        return self._filter_aeroplanes(
            aeroplanes,
            criteria,
        )

    @staticmethod
    def _filter_aeroplanes(
        aeroplanes: list[Aeroplane],
        criteria: dict[str, Any],
    ) -> list[Aeroplane]:
        """Отфильтровать самолёты."""

        result = aeroplanes

        if "origin_country" in criteria:
            country = criteria["origin_country"]

            if not isinstance(country, str):
                raise TypeError(
                    "Страна должна быть строкой."
                )

            result = [
                plane
                for plane in result
                if plane.origin_country.lower() == country.lower()
            ]

        if "min_altitude" in criteria:
            min_altitude = criteria["min_altitude"]

            if not isinstance(
                min_altitude,
                (int, float),
            ):
                raise TypeError(
                    "Минимальная высота должна быть числом."
                )

            result = [
                plane
                for plane in result
                if plane.altitude >= min_altitude
            ]

        if "max_altitude" in criteria:
            max_altitude = criteria["max_altitude"]

            if not isinstance(
                max_altitude,
                (int, float),
            ):
                raise TypeError(
                    "Максимальная высота должна быть числом."
                )

            result = [
                plane
                for plane in result
                if plane.altitude <= max_altitude
            ]

        return result

    def delete_aeroplane(
        self,
        aeroplane: Aeroplane,
    ) -> bool:
        """Удалить самолёт по ICAO24."""

        if not isinstance(aeroplane, Aeroplane):
            raise TypeError(
                "Удалить можно только объект Aeroplane."
            )

        data = self._read_data()

        new_data = [
            item
            for item in data
            if item.get("icao24") != aeroplane.icao24
        ]

        if len(new_data) == len(data):
            return False

        self._write_data(new_data)

        return True