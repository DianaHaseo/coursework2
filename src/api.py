import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

import requests
from dotenv import load_dotenv


load_dotenv()


class APIError(Exception):
    """Ошибка при работе с внешним API."""


class BaseAPI(ABC):
    """Абстрактный класс для работы с внешними API."""

    @abstractmethod
    def get_country_bounding_box(
        self,
        country: str,
    ) -> tuple[float, float, float, float]:
        """Получить bounding box страны."""

    @abstractmethod
    def get_aeroplanes(
        self,
        country: str,
    ) -> list[list[Any]]:
        """Получить данные о самолётах над страной."""


class AeroplanesAPI(BaseAPI):
    """Класс для получения информации о странах и самолётах."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"
    TOKEN_URL = (
        "https://auth.opensky-network.org/"
        "auth/realms/opensky-network/"
        "protocol/openid-connect/token"
    )

    def __init__(self, timeout: int = 10) -> None:
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError(
                "Таймаут должен быть положительным целым числом."
            )

        self.timeout = timeout

        self.headers = {
            "User-Agent": "coursework-aeroplanes/1.0"
        }

        self.client_id = os.getenv("OPENSKY_CLIENT_ID")
        self.client_secret = os.getenv("OPENSKY_CLIENT_SECRET")

        if not self.client_id:
            raise APIError(
                "Не задана переменная OPENSKY_CLIENT_ID."
            )

        if not self.client_secret:
            raise APIError(
                "Не задана переменная OPENSKY_CLIENT_SECRET."
            )

        self.opensky_token: str | None = None
        self.token_expires_at: datetime | None = None

    def _get_opensky_token(self) -> str:
        """Получить новый OAuth2-токен OpenSky."""

        if (
            self.opensky_token
            and self.token_expires_at
            and datetime.now() < self.token_expires_at
        ):
            return self.opensky_token

        try:
            response = requests.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as error:
            raise APIError(
                f"Ошибка получения токена OpenSky: {error}"
            ) from error

        try:
            data = response.json()
        except ValueError as error:
            raise APIError(
                "OpenSky вернул некорректный ответ "
                "при получении токена."
            ) from error

        token = data.get("access_token")

        if not isinstance(token, str) or not token:
            raise APIError(
                "OpenSky не вернул access_token."
            )

        expires_in = data.get("expires_in", 1800)

        try:
            expires_in = int(expires_in)
        except (TypeError, ValueError):
            expires_in = 1800

        self.opensky_token = token

        self.token_expires_at = (
            datetime.now()
            + timedelta(seconds=max(expires_in - 30, 1))
        )

        return token

    def _request_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Выполнить GET-запрос и вернуть JSON."""

        request_headers = (
            headers.copy()
            if headers
            else self.headers.copy()
        )

        if "opensky-network.org" in url:
            token = self._get_opensky_token()
            request_headers["Authorization"] = (
                f"Bearer {token}"
            )

        try:
            response = requests.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as error:
            raise APIError(
                f"Ошибка при обращении к API: {error}"
            ) from error

        try:
            return response.json()
        except ValueError as error:
            raise APIError(
                "API вернул некорректный JSON."
            ) from error

    def get_country_bounding_box(
        self,
        country: str,
    ) -> tuple[float, float, float, float]:
        """Получить координаты границ страны."""

        if not isinstance(country, str) or not country.strip():
            raise ValueError(
                "Название страны не должно быть пустым."
            )

        params = {
            "q": country.strip(),
            "format": "jsonv2",
            "limit": 1,
            "addressdetails": 1,
        }

        data = self._request_json(
            self.NOMINATIM_URL,
            params=params,
        )

        if not isinstance(data, list) or not data:
            raise APIError(
                f"Страна '{country}' не найдена."
            )

        bounding_box = data[0].get("boundingbox")

        if (
            not isinstance(bounding_box, list)
            or len(bounding_box) != 4
        ):
            raise APIError(
                "API Nominatim не вернул корректный "
                "boundingbox."
            )

        try:
            south = float(bounding_box[0])
            north = float(bounding_box[1])
            west = float(bounding_box[2])
            east = float(bounding_box[3])
        except (TypeError, ValueError) as error:
            raise APIError(
                "Координаты boundingbox имеют "
                "некорректный формат."
            ) from error

        return south, north, west, east

    def get_aeroplanes(
        self,
        country: str,
    ) -> list[list[Any]]:
        """Получить самолёты над страной."""

        south, north, west, east = (
            self.get_country_bounding_box(country)
        )

        params = {
            "lamin": south,
            "lomin": west,
            "lamax": north,
            "lomax": east,
        }

        data = self._request_json(
            self.OPENSKY_URL,
            params=params,
        )

        if not isinstance(data, dict):
            raise APIError(
                "API OpenSky вернул данные "
                "в некорректном формате."
            )

        states = data.get("states")

        if states is None:
            return []

        if not isinstance(states, list):
            raise APIError(
                "Поле states имеет некорректный формат."
            )

        return states