from src.mapping.rts22_fields import RTS22_FIELDS


def test_has_all_65_fields():
    assert len(RTS22_FIELDS) == 65


def test_field_numbers_are_unique():
    numbers = [f["number"] for f in RTS22_FIELDS]
    assert len(numbers) == len(set(numbers))


def test_field_numbers_cover_1_to_65_with_no_gaps():
    numbers = [f["number"] for f in RTS22_FIELDS]
    assert sorted(numbers) == list(range(1, 66))