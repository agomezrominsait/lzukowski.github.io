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
    s = mock.Mock()
    s.is_domestic = True
    return s


@pytest.mark.parametrize("phone", [
    None, '', '344546234', '0 44 72453', '+44 072453', '+44472453',
])
def test_providing_phone_for_domestic_shipment(
        phone, service, shipment, gb_default_phone,
):
    shipment.shipping_address.phone = phone
    assert shipment.is_domestic is True

    service.provide(shipment, 'GB')

    assert shipment.shipping_address.phone == gb_default_phone


@pytest.mark.parametrize("phone, expected_phone", [
    ('0 7  344546234', '07344546234'),
    ('7 344546234', '07344546234'),
    ('+ 44 72453', '072453'),
    ('0 044 72453', '072453'),
])
def test_not_providing_phone_for_domestic_shipment(
        phone, expected_phone, service, shipment,
):
    shipment.shipping_address.phone = phone
    assert shipment.is_domestic is True

    service.provide(shipment, 'GB')

    assert shipment.shipping_address.phone == expected_phone


def test_not_providing_phone_for_domestic_shipment_if_no_default_set(
        service, shipment,
):
    shipment.shipping_address.phone = None

    service.provide(shipment, 'PL')

    assert shipment.shipping_address.phone is None
