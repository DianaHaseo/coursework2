import json

import pytest

from src.aeroplane import Aeroplane
from src.file_saver import JSONSaver, StorageError


@pytest.fixture
def plane() -> Aeroplane:
    return Aeroplane(
        "abcdef",
        "TEST123",
        "Germany",
        250,
        10000,
    )


@pytest.fixture
def second_plane() -> Aeroplane:
    return Aeroplane(
        "123456",
        "TEST456",
        "France",
        200,
        8000,
    )


def test_json_saver_creates_file(tmp_path):
    file_path = tmp_path / "planes.json"

    saver = JSONSaver(file_path)

    assert file_path.exists()
    assert saver.get_aeroplanes() == []


def test_add_aeroplane(tmp_path, plane):
    file_path = tmp_path / "planes.json"

    saver = JSONSaver(file_path)
    saver.add_aeroplane(plane)

    result = saver.get_aeroplanes()

    assert len(result) == 1
    assert result[0].icao24 == "abcdef"


def test_duplicate_aeroplane_not_added(
    tmp_path,
    plane,
):
    file_path = tmp_path / "planes.json"

    saver = JSONSaver(file_path)

    saver.add_aeroplane(plane)
    saver.add_aeroplane(plane)

    result = saver.get_aeroplanes()

    assert len(result) == 1


def test_add_wrong_type(tmp_path):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    with pytest.raises(TypeError):
        saver.add_aeroplane("plane")


def test_get_aeroplanes_by_country(
    tmp_path,
    plane,
    second_plane,
):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    saver.add_aeroplane(plane)
    saver.add_aeroplane(second_plane)

    result = saver.get_aeroplanes(
        {"origin_country": "Germany"}
    )

    assert len(result) == 1
    assert result[0].origin_country == "Germany"


def test_get_aeroplanes_by_min_altitude(
    tmp_path,
    plane,
    second_plane,
):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    saver.add_aeroplane(plane)
    saver.add_aeroplane(second_plane)

    result = saver.get_aeroplanes(
        {"min_altitude": 9000}
    )

    assert len(result) == 1
    assert result[0].icao24 == "abcdef"


def test_get_aeroplanes_by_max_altitude(
    tmp_path,
    plane,
    second_plane,
):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    saver.add_aeroplane(plane)
    saver.add_aeroplane(second_plane)

    result = saver.get_aeroplanes(
        {"max_altitude": 9000}
    )

    assert len(result) == 1
    assert result[0].icao24 == "123456"


def test_invalid_country_criteria(tmp_path):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    with pytest.raises(TypeError):
        saver.get_aeroplanes(
            {"origin_country": 123}
        )


def test_invalid_min_altitude_criteria(tmp_path):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    with pytest.raises(TypeError):
        saver.get_aeroplanes(
            {"min_altitude": "high"}
        )


def test_delete_aeroplane(
    tmp_path,
    plane,
):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    saver.add_aeroplane(plane)

    result = saver.delete_aeroplane(plane)

    assert result is True
    assert saver.get_aeroplanes() == []


def test_delete_missing_aeroplane(
    tmp_path,
    plane,
):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    result = saver.delete_aeroplane(plane)

    assert result is False


def test_delete_wrong_type(tmp_path):
    saver = JSONSaver(
        tmp_path / "planes.json"
    )

    with pytest.raises(TypeError):
        saver.delete_aeroplane("plane")


def test_invalid_json(tmp_path):
    file_path = tmp_path / "planes.json"

    file_path.write_text(
        "{invalid json}",
        encoding="utf-8",
    )

    saver = JSONSaver(file_path)

    with pytest.raises(StorageError):
        saver.get_aeroplanes()


def test_json_is_valid(
    tmp_path,
    plane,
):
    file_path = tmp_path / "planes.json"

    saver = JSONSaver(file_path)
    saver.add_aeroplane(plane)

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert isinstance(data, list)
    assert data[0]["icao24"] == "abcdef"