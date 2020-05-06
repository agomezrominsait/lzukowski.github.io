from typing import Dict, Text

import pytest

from phone_provider import Country, Phone, PhoneProvider


class DummyParameterService:
    def __init__(self, country_phones: Dict[Country, Phone]):
        self._phones = {
            f'default_phone_for_domestic_{country}': phone
            for country, phone in country_phones.items()
        }

    def get(self, key: Text) -> Text:
        phone = self._phones.get(key)
        if not phone:
            raise FileNotFoundError(key)
        return phone


@pytest.fixture
def gb_default_phone():
    return Phone('07346923435')


@pytest.fixture
def service(gb_default_phone):
    parameter_service = DummyParameterService(
        {Country('GB'): Phone(gb_default_phone)}
    )
    return PhoneProvider(parameter_service.get)


class TestPhoneProvider:
    @pytest.mark.parametrize("invalid_phone", [
        None,
        Phone(''),
        Phone('344546234'),
        Phone('0 44 72453'),
        Phone('+44 072453'),
        Phone('+44472453'),
    ])
    def test_default_gb_phone_when_invalid_phone_in_gb_shipment(
            self, invalid_phone, service, gb_default_phone,
    ):
        assert service.provide(invalid_phone, Country('GB')) == gb_default_phone

    @pytest.mark.parametrize("valid_phone", [
        Phone('07344546234'),
        Phone('072453'),
    ])
    def test_no_changing_shipping_phone_when_valid_gb_phone(
            self, valid_phone, service,
    ):
        assert service.provide(valid_phone, Country('GB')) == valid_phone

    @pytest.mark.parametrize("phone, country", [
        (None, 'PL'),
        (None, 'DE'),
        (None, 'FR'),
        (Phone('0 7  344546234'), 'PL'),
        (Phone('7 344546234'), 'DE'),
        (Phone('+ 44 72453'), 'FR'),
        (Phone('0 044 72453'), 'US'),
    ])
    def test_not_changing_shipping_added_phone_when_not_gb_shipment(
            self, service, phone, country,
    ):
        assert service.provide(phone, Country('PL')) == phone


class TestPhoneNormalization:
    @pytest.mark.parametrize("phone, normalized_phone", [
        (Phone('0 7  344546234'), '07344546234'),
        (Phone('7 344546234'), '07344546234'),
    ])
    def test_number_normalization_when_valid_gb_phone(
            self, phone, normalized_phone, service,
    ):
        assert service.provide(phone, Country('GB')) == normalized_phone

    @pytest.mark.parametrize("phone, normalized_phone", [
        (Phone('+ 44 72453'), '072453'),
        (Phone('0 044 72453'), '072453'),
    ])
    def test_remove_country_prefix(self, phone, normalized_phone, service):
        assert service.provide(phone, Country('GB')) == normalized_phone
