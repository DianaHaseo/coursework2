from typing import Any


class Aeroplane:
    """Модель самолёта."""

    def __init__(
        self,
        icao24: str,
        callsign: str,
        origin_country: str,
        velocity: float,
        altitude: float,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        self.icao24 = self._validate_icao24(icao24)
        self.callsign = self._validate_text(callsign, "Позывной")
        self.origin_country = self._validate_text(
            origin_country,
            "Страна регистрации",
        )

        self._velocity = self._validate_non_negative_number(
            velocity,
            "Скорость",
        )

        self._altitude = self._validate_non_negative_number(
            altitude,
            "Высота",
        )

        self.latitude = self._validate_coordinate(
            latitude,
            -90,
            90,
            "Широта",
        )

        self.longitude = self._validate_coordinate(
            longitude,
            -180,
            180,
            "Долгота",
        )

    @staticmethod
    def _validate_text(value: str, field_name: str) -> str:
        """Проверить строковое значение."""

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} должен быть строкой."
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"{field_name} не должен быть пустым."
            )

        return value

    @staticmethod
    def _validate_icao24(value: str) -> str:
        """Проверить ICAO24."""

        if not isinstance(value, str):
            raise TypeError("ICAO24 должен быть строкой.")

        value = value.strip().lower()

        if not value:
            raise ValueError("ICAO24 не должен быть пустым.")

        if len(value) != 6:
            raise ValueError(
                "ICAO24 должен содержать 6 символов."
            )

        try:
            int(value, 16)
        except ValueError as error:
            raise ValueError(
                "ICAO24 должен содержать шестнадцатеричные символы."
            ) from error

        return value

    @staticmethod
    def _validate_non_negative_number(
        value: float,
        field_name: str,
    ) -> float:
        """Проверить числовое значение."""

        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise TypeError(
                f"{field_name} должен быть числом."
            )

        if value < 0:
            raise ValueError(
                f"{field_name} не может быть отрицательной."
            )

        return float(value)

    @staticmethod
    def _validate_coordinate(
        value: float | None,
        minimum: float,
        maximum: float,
        field_name: str,
    ) -> float | None:
        """Проверить координату."""

        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise TypeError(
                f"{field_name} должна быть числом или None."
            )

        if not minimum <= value <= maximum:
            raise ValueError(
                f"{field_name} должна быть от "
                f"{minimum} до {maximum}."
            )

        return float(value)

    @property
    def velocity(self) -> float:
        """Скорость самолёта."""

        return self._velocity

    @velocity.setter
    def velocity(self, value: float) -> None:
        self._velocity = self._validate_non_negative_number(
            value,
            "Скорость",
        )

    @property
    def altitude(self) -> float:
        """Высота самолёта."""

        return self._altitude

    @altitude.setter
    def altitude(self, value: float) -> None:
        self._altitude = self._validate_non_negative_number(
            value,
            "Высота",
        )

    def is_faster_than(self, other: "Aeroplane") -> bool:
        """Проверить, быстрее ли этот самолёт другого."""

        if not isinstance(other, Aeroplane):
            raise TypeError(
                "Сравнивать можно только с объектом Aeroplane."
            )

        return self.velocity > other.velocity

    def is_higher_than(self, other: "Aeroplane") -> bool:
        """Проверить, находится ли этот самолёт выше другого."""

        if not isinstance(other, Aeroplane):
            raise TypeError(
                "Сравнивать можно только с объектом Aeroplane."
            )

        return self.altitude > other.altitude

    def compare_by_speed(self, other: "Aeroplane") -> int:
        """
        Сравнить самолёты по скорости.

        1  -> этот самолёт быстрее
        0  -> скорости одинаковые
        -1 -> этот самолёт медленнее
        """

        if not isinstance(other, Aeroplane):
            raise TypeError(
                "Сравнивать можно только с объектом Aeroplane."
            )

        if self.velocity > other.velocity:
            return 1

        if self.velocity < other.velocity:
            return -1

        return 0

    def compare_by_altitude(self, other: "Aeroplane") -> int:
        """
        Сравнить самолёты по высоте.

        1  -> этот самолёт выше
        0  -> высота одинаковая
        -1 -> этот самолёт ниже
        """

        if not isinstance(other, Aeroplane):
            raise TypeError(
                "Сравнивать можно только с объектом Aeroplane."
            )

        if self.altitude > other.altitude:
            return 1

        if self.altitude < other.altitude:
            return -1

        return 0

    def to_dict(self) -> dict[str, Any]:
        """Преобразовать объект в словарь."""

        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "altitude": self.altitude,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    @classmethod
    def from_open_sky_state(
        cls,
        state: list[Any],
    ) -> "Aeroplane":
        """Создать Aeroplane из state OpenSky."""

        if not isinstance(state, list):
            raise TypeError(
                "Данные самолёта должны быть списком."
            )

        if len(state) < 11:
            raise ValueError(
                "В данных OpenSky недостаточно информации."
            )

        icao24 = state[0]
        callsign = state[1] or "UNKNOWN"
        origin_country = state[2] or "UNKNOWN"

        longitude = state[5]
        latitude = state[6]
        altitude = state[7]
        velocity = state[9]

        if velocity is None:
            velocity = 0.0

        if altitude is None:
            altitude = 0.0

        return cls(
            icao24=icao24,
            callsign=callsign.strip(),
            origin_country=origin_country,
            velocity=velocity,
            altitude=altitude,
            latitude=latitude,
            longitude=longitude,
        )

    @classmethod
    def cast_to_object_list(
        cls,
        states: list[list[Any]],
    ) -> list["Aeroplane"]:
        """Преобразовать список states в список объектов Aeroplane."""

        if not isinstance(states, list):
            raise TypeError(
                "States должны быть представлены списком."
            )

        aeroplanes = []

        for state in states:
            try:
                aeroplane = cls.from_open_sky_state(state)
            except (TypeError, ValueError):
                continue

            aeroplanes.append(aeroplane)

        return aeroplanes

    def __str__(self) -> str:
        return (
            f"{self.callsign} | "
            f"Страна: {self.origin_country} | "
            f"Скорость: {self.velocity:.2f} м/с | "
            f"Высота: {self.altitude:.2f} м"
        )

