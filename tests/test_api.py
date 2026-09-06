from unittest.mock import Mock, patch

import pytest
import requests

from src.api import APIError, AeroplanesAPI, BaseAPI


def test_base_api_is_abstract():
    with pytest.raises(TypeError):
        BaseAPI()


def test_invalid_timeout():
    with pytest.raises(ValueError):
        AeroplanesAPI(0)


def test_empty_country():
    api = AeroplanesAPI()

    with pytest.raises(ValueError):
        api.get_country_bounding_box("")


def test_whitespace_country():
    api = AeroplanesAPI()

    with pytest.raises(ValueError):
        api.get_country_bounding_box("   ")


@patch("src.api.requests.get")
def test_get_country_bounding_box(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = [
        {
            "boundingbox": [
                "40.0",
                "45.0",
                "10.0",
                "20.0",
            ]
        }
    ]

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    result = api.get_country_bounding_box(
        "Test Country"
    )

    assert result == (
        40.0,
        45.0,
        10.0,
        20.0,
    )

    mock_get.assert_called_once()


@patch("src.api.requests.get")
def test_country_not_found(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = []
    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    with pytest.raises(APIError):
        api.get_country_bounding_box(
            "Unknown Country"
        )


@patch("src.api.requests.get")
def test_invalid_bounding_box(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = [
        {
            "boundingbox": [
                "1",
                "2",
            ]
        }
    ]

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    with pytest.raises(APIError):
        api.get_country_bounding_box(
            "Test Country"
        )


@patch("src.api.requests.get")
def test_request_exception(mock_get):
    mock_get.side_effect = requests.RequestException(
        "Connection error"
    )

    api = AeroplanesAPI()

    with pytest.raises(APIError):
        api.get_country_bounding_box(
            "Germany"
        )


@patch("src.api.requests.get")
def test_invalid_json(mock_get):
    mock_response = Mock()

    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = ValueError()

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    with pytest.raises(APIError):
        api.get_country_bounding_box(
            "Germany"
        )


@patch("src.api.requests.get")
def test_get_aeroplanes(mock_get):
    mock_response = Mock()

    mock_response.raise_for_status.return_value = None

    mock_response.json.side_effect = [
        [
            {
                "boundingbox": [
                    "40",
                    "45",
                    "10",
                    "20",
                ]
            }
        ],
        {
            "states": [
                [
                    "abcdef",
                    "TEST123",
                    "Germany",
                    1,
                    2,
                    15,
                    42,
                    10000,
                    False,
                    250,
                    180,
                ]
            ]
        },
    ]

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    result = api.get_aeroplanes(
        "Germany"
    )

    assert len(result) == 1
    assert result[0][0] == "abcdef"


@patch("src.api.requests.get")
def test_get_aeroplanes_without_states(mock_get):
    mock_response = Mock()

    mock_response.raise_for_status.return_value = None

    mock_response.json.side_effect = [
        [
            {
                "boundingbox": [
                    "40",
                    "45",
                    "10",
                    "20",
                ]
            }
        ],
        {},
    ]

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    result = api.get_aeroplanes(
        "Germany"
    )

    assert result == []


@patch("src.api.requests.get")
def test_get_aeroplanes_invalid_response(mock_get):
    mock_response = Mock()

    mock_response.raise_for_status.return_value = None

    mock_response.json.side_effect = [
        [
            {
                "boundingbox": [
                    "40",
                    "45",
                    "10",
                    "20",
                ]
            }
        ],
        [],
    ]

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    with pytest.raises(APIError):
        api.get_aeroplanes(
            "Germany"
        )


@patch("src.api.requests.get")
def test_get_aeroplanes_invalid_states(mock_get):
    mock_response = Mock()

    mock_response.raise_for_status.return_value = None

    mock_response.json.side_effect = [
        [
            {
                "boundingbox": [
                    "40",
                    "45",
                    "10",
                    "20",
                ]
            }
        ],
        {
            "states": "wrong"
        },
    ]

    mock_get.return_value = mock_response

    api = AeroplanesAPI()

    with pytest.raises(APIError):
        api.get_aeroplanes(
            "Germany"
        )