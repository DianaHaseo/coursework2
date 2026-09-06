import pytest

from src.aeroplane import Aeroplane


@pytest.fixture
def aeroplane() -> Aeroplane:
    return Aeroplane(
        "abcdef",
        "UAL123",
        "United States",
        250.0,
        10000.0,
        40.0,
        -74.0,
    )


@pytest.fixture
def slower_plane() -> Aeroplane:
    return Aeroplane(
        "123456",
        "DLH456",
        "Germany",
        200.0,
        9000.0,
        50.0,
        8.0,
    )


def test_aeroplane_init(aeroplane):
    assert aeroplane.icao24 == "abcdef"
    assert aeroplane.callsign == "UAL123"
    assert aeroplane.origin_country == "United States"
    assert aeroplane.velocity == 250.0
    assert aeroplane.altitude == 10000.0
    assert aeroplane.latitude == 40.0
    assert aeroplane.longitude == -74.0


def test_velocity_property(aeroplane):
    aeroplane.velocity = 300

    assert aeroplane.velocity == 300.0


def test_altitude_property(aeroplane):
    aeroplane.altitude = 12000

    assert aeroplane.altitude == 12000.0


def test_negative_velocity():
    with pytest.raises(ValueError):
        Aeroplane(
            "abcdef",
            "TEST",
            "Germany",
            -1,
            10000,
        )


def test_negative_altitude():
    with pytest.raises(ValueError):
        Aeroplane(
            "abcdef",
            "TEST",
            "Germany",
            100,
            -1,
        )


def test_invalid_icao24():
    with pytest.raises(ValueError):
        Aeroplane(
            "wrong",
            "TEST",
            "Germany",
            100,
            10000,
        )


def test_invalid_country():
    with pytest.raises(ValueError):
        Aeroplane(
            "abcdef",
            "TEST",
            "",
            100,
            10000,
        )


def test_invalid_velocity_type():
    with pytest.raises(TypeError):
        Aeroplane(
            "abcdef",
            "TEST",
            "Germany",
            "fast",
            10000,
        )


def test_invalid_altitude_type():
    with pytest.raises(TypeError):
        Aeroplane(
            "abcdef",
            "TEST",
            "Germany",
            100,
            "high",
        )


def test_invalid_latitude():
    with pytest.raises(ValueError):
        Aeroplane(
            "abcdef",
            "TEST",
            "Germany",
            100,
            10000,
            100,
        )


def test_invalid_longitude():
    with pytest.raises(ValueError):
        Aeroplane(
            "abcdef",
            "TEST",
            "Germany",
            100,
            10000,
            50,
            200,
        )


def test_is_faster_than(aeroplane, slower_plane):
    assert aeroplane.is_faster_than(slower_plane)
    assert not slower_plane.is_faster_than(aeroplane)


def test_is_higher_than(aeroplane, slower_plane):
    assert aeroplane.is_higher_than(slower_plane)
    assert not slower_plane.is_higher_than(aeroplane)


def test_compare_by_speed(aeroplane, slower_plane):
    assert aeroplane.compare_by_speed(slower_plane) == 1
    assert slower_plane.compare_by_speed(aeroplane) == -1


def test_compare_equal_speed(aeroplane):
    other = Aeroplane(
        "123456",
        "TEST",
        "Germany",
        250,
        9000,
    )

    assert aeroplane.compare_by_speed(other) == 0


def test_compare_by_altitude(aeroplane, slower_plane):
    assert aeroplane.compare_by_altitude(slower_plane) == 1
    assert slower_plane.compare_by_altitude(aeroplane) == -1


def test_compare_equal_altitude(aeroplane):
    other = Aeroplane(
        "123456",
        "TEST",
        "Germany",
        200,
        10000,
    )

    assert aeroplane.compare_by_altitude(other) == 0


def test_comparison_with_wrong_type(aeroplane):
    with pytest.raises(TypeError):
        aeroplane.is_faster_than("plane")

    with pytest.raises(TypeError):
        aeroplane.is_higher_than("plane")


def test_to_dict(aeroplane):
    result = aeroplane.to_dict()

    assert result["icao24"] == "abcdef"
    assert result["callsign"] == "UAL123"
    assert result["velocity"] == 250.0


def test_from_open_sky_state():
    state = [
        "abcdef",
        "UAL123",
        "United States",
        1234567890,
        1234567891,
        -74.0,
        40.0,
        10000.0,
        False,
        250.0,
        180.0,
    ]

    plane = Aeroplane.from_open_sky_state(state)

    assert plane.icao24 == "abcdef"
    assert plane.callsign == "UAL123"
    assert plane.velocity == 250.0
    assert plane.altitude == 10000.0


def test_from_open_sky_state_with_none_values():
    state = [
        "abcdef",
        None,
        None,
        None,
        1234567891,
        None,
        None,
        None,
        True,
        None,
        None,
    ]

    plane = Aeroplane.from_open_sky_state(state)

    assert plane.callsign == "UNKNOWN"
    assert plane.origin_country == "UNKNOWN"
    assert plane.velocity == 0
    assert plane.altitude == 0


def test_invalid_open_sky_state():
    with pytest.raises(ValueError):
        Aeroplane.from_open_sky_state([])


def test_cast_to_object_list():
    states = [
        [
            "abcdef",
            "TEST1",
            "Germany",
            1,
            2,
            10,
            50,
            10000,
            False,
            200,
            180,
        ],
        [
            "123456",
            "TEST2",
            "France",
            1,
            2,
            20,
            40,
            9000,
            False,
            250,
            180,
        ],
    ]

    result = Aeroplane.cast_to_object_list(states)

    assert len(result) == 2
    assert all(
        isinstance(plane, Aeroplane)
        for plane in result
    )


def test_str(aeroplane):
    result = str(aeroplane)

    assert "UAL123" in result
    assert "United States" in result
    assert "250.00" in result
    assert "10000.00" in result