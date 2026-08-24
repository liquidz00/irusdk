"""Unit tests for model validation, normalization, and derived fields."""

from datetime import datetime, timedelta, timezone

import pytest

from irusdk.models import Blueprint, Device, Model, User
from irusdk.models.devices import Device as DeviceFromSubmodule


def test_models_are_importable_from_the_package() -> None:
    assert Device is DeviceFromSubmodule


@pytest.mark.parametrize("blank", ["", "   ", "\t\n"])
def test_blank_strings_become_none(blank: str) -> None:
    device = Device.model_validate({"asset_tag": blank, "lost_mode_status": blank})
    assert device.asset_tag is None
    assert device.lost_mode_status is None


def test_real_strings_survive_normalization() -> None:
    device = Device.model_validate({"asset_tag": "AH-0042", "lost_mode_status": "PENDING"})
    assert device.asset_tag == "AH-0042"
    assert device.lost_mode_status == "PENDING"


def test_blank_strings_become_none_across_models() -> None:
    user = User.model_validate({"department": "", "job_title": "IT"})
    blueprint = Blueprint.model_validate({"description": "  ", "name": "main hive"})
    assert user.department is None
    assert user.job_title == "IT"
    assert blueprint.description is None
    assert blueprint.name == "main hive"


@pytest.mark.parametrize(
    ("os_version", "expected_major", "expected_info"),
    [
        ("14.4.1", 14, (14, 4, 1)),
        ("26.0", 26, (26, 0)),
        ("9.2", 9, (9, 2)),
        ("15", 15, (15,)),
        ("14.4.1 (23E224)", 14, (14, 4)),
        ("  17.1  ", 17, (17, 1)),
        (None, None, ()),
        ("", None, ()),
        ("unknown", None, ()),
    ],
)
def test_parses_os_versions(
    os_version: str | None, expected_major: int | None, expected_info: tuple[int, ...]
) -> None:
    device = Device.model_validate({"os_version": os_version})
    assert device.os_major == expected_major
    assert device.os_version_info == expected_info


def test_os_versions_compare_by_number_not_string() -> None:
    older = Device.model_validate({"os_version": "9.2"})
    newer = Device.model_validate({"os_version": "15.1"})
    assert newer.os_version_info > older.os_version_info
    assert newer.os_version < older.os_version  # the bug this exists to avoid


def test_days_since_check_in() -> None:
    seen = datetime.now(timezone.utc) - timedelta(days=5, hours=1)
    device = Device.model_validate({"last_check_in": seen.isoformat()})
    assert device.days_since_check_in == 5


def test_days_since_check_in_assumes_utc_when_unzoned() -> None:
    seen = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=3)
    device = Device.model_validate({"last_check_in": seen.isoformat()})
    assert device.days_since_check_in == 3


def test_days_since_check_in_without_a_check_in() -> None:
    assert Device.model_validate({}).days_since_check_in is None


@pytest.mark.parametrize(
    ("assigned", "missing", "count", "percent"),
    [
        (100, 25, 75, 75.0),
        (8, 1, 7, 87.5),
        (10, 0, 10, 100.0),
        (10, None, 10, 100.0),
        (0, 0, 0, None),
        (None, 3, None, None),
        (5, 9, 0, 0.0),
    ],
)
def test_blueprint_presence_math(
    assigned: int | None, missing: int | None, count: int | None, percent: float | None
) -> None:
    blueprint = Blueprint.model_validate(
        {"computers_count": assigned, "missing_computers_count": missing}
    )
    assert blueprint.present_count == count
    assert blueprint.present_percent == percent


def test_computed_fields_serialize_and_time_dependent_ones_do_not() -> None:
    dumped = Device.model_validate({"os_version": "14.4.1", "last_check_in": None}).model_dump()
    assert dumped["os_major"] == 14
    assert "days_since_check_in" not in dumped
    assert "os_version_info" not in dumped

    assert Blueprint.model_validate({"computers_count": 4}).model_dump()["present_percent"] == 100.0


def test_unknown_fields_are_preserved_and_reportable() -> None:
    device = Device.model_validate({"device_name": "Test Mac", "brand_new_iru_field": 42})
    assert device.unknown_fields == {"brand_new_iru_field": 42}
    assert device.brand_new_iru_field == 42


def test_unknown_fields_is_empty_for_a_known_payload() -> None:
    assert Device.model_validate({"device_name": "Test Mac"}).unknown_fields == {}


def test_base_model_allows_extras() -> None:
    assert Model.model_validate({"anything": 1}).unknown_fields == {"anything": 1}
