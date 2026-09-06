import pytest

from src.aeroplane import Aeroplane
from src.utils import (
    filter_aeroplanes_by_country,
    get_top_aeroplanes,
    sort_aeroplanes_by_altitude,
)


@pytest.fixture
def aeroplanes() -> list[Aeroplane]:
    return [
        Aeroplane(
            "abcdef",
            "PLANE1",
            "Germany",
            200,
            8000,
        ),
        Aeroplane(
            "123456",
            "PLANE2",
            "France",
            250,
            12000,
        ),
        Aeroplane(
            "654321",
            "PLANE3",
            "Germany",
            220,
            10000,
        ),
    ]


def test_filter_by_country(aeroplanes):
    result = filter_aeroplanes_by_country(
        aeroplanes,
        ["Germany"],
    )

    assert len(result) == 2
    assert all(
        plane.origin_country == "Germany"
        for plane in result
    )


def test_filter_by_multiple_countries(aeroplanes):
    result = filter_aeroplanes_by_country(
        aeroplanes,
        ["Germany", "France"],
    )

    assert len(result) == 3


def test_filter_case_insensitive(aeroplanes):
    result = filter_aeroplanes_by_country(
        aeroplanes,
        ["gErMaNy"],
    )

    assert len(result) == 2


def test_filter_invalid_aeroplanes():
    with pytest.raises(TypeError):
        filter_aeroplanes_by_country(
            "wrong",
            ["Germany"],
        )


def test_filter_invalid_countries(aeroplanes):
    with pytest.raises(TypeError):
        filter_aeroplanes_by_country(
            aeroplanes,
            "Germany",
        )


def test_filter_empty_countries(aeroplanes):
    with pytest.raises(ValueError):
        filter_aeroplanes_by_country(
            aeroplanes,
            [],
        )


def test_sort_by_altitude(aeroplanes):
    result = sort_aeroplanes_by_altitude(
        aeroplanes
    )

    assert [
        plane.altitude
        for plane in result
    ] == [12000, 10000, 8000]


def test_sort_invalid_data():
    with pytest.raises(TypeError):
        sort_aeroplanes_by_altitude("wrong")


def test_get_top_n(aeroplanes):
    result = get_top_aeroplanes(
        aeroplanes,
        2,
    )

    assert len(result) == 2

    assert [
        plane.altitude
        for plane in result
    ] == [12000, 10000]


def test_get_top_more_than_length(aeroplanes):
    result = get_top_aeroplanes(
        aeroplanes,
        100,
    )

    assert len(result) == 3


def test_get_top_invalid_n(aeroplanes):
    with pytest.raises(ValueError):
        get_top_aeroplanes(
            aeroplanes,
            0,
        )


def test_get_top_negative_n(aeroplanes):
    with pytest.raises(ValueError):
        get_top_aeroplanes(
            aeroplanes,
            -1,
        )


def test_get_top_wrong_type(aeroplanes):
    with pytest.raises(TypeError):
        get_top_aeroplanes(
            aeroplanes,
            "5",
        )

