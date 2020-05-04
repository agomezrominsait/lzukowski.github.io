from typing import Dict, NewType, Text
from unittest import mock

import pytest

from phone_provider import PhoneProvider


Country = NewType('Country', Text)
Phone = NewType('Phone', Text)


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
    return '07346923435'


@pytest.fixture
def service(gb_default_phone):
    parameter_service = DummyParameterService(
        {Country('GB'): Phone(gb_default_phone)}
    )
    return PhoneProvider(parameter_service.get)


@pytest.fixture
def shipment():
    return mock.Mock(is_domestic=True, shipping_address=mock.Mock(phone=None))


@pytest.mark.parametrize("invalid_phone", [
    None, '', '344546234', '0 44 72453', '+44 072453', '+44472453',
])
def test_default_gb_phone_when_invalid_phone_in_gb_shipment(
        invalid_phone, service, shipment, gb_default_phone,
):
    shipment.shipping_address.phone = invalid_phone
    service.provide(shipment, 'GB')
    assert shipment.shipping_address.phone == gb_default_phone


@pytest.mark.parametrize("phone, normalized_phone", [
    ('0 7  344546234', '07344546234'),
    ('7 344546234', '07344546234'),
    ('+ 44 72453', '072453'),
    ('0 044 72453', '072453'),
])
def test_number_normalization_when_valid_gb_phone(
        phone, normalized_phone, service, shipment,
):
    shipment.shipping_address.phone = phone
    service.provide(shipment, 'GB')
    assert shipment.shipping_address.phone == normalized_phone


@pytest.mark.parametrize("phone, country", [
    (None, 'PL'),
    (None, 'DE'),
    (None, 'FR'),
    ('0 7  344546234', 'PL'),
    ('7 344546234', 'DE'),
    ('+ 44 72453', 'FR'),
    ('0 044 72453', 'US'),
])
def test_not_changing_shipping_added_phone_when_not_gb_shipment(
        service, shipment, phone, country,
):
    shipment.shipping_address.phone = phone
    service.provide(shipment, 'PL')
    assert shipment.shipping_address.phone == phone
