from unittest import mock
from unittest.mock import call

import pytest

from phone_provider import PhoneProvider


@pytest.fixture
def get_parameter_service():
    return mock.Mock()


@pytest.fixture
def service(get_parameter_service):
    return PhoneProvider(get_parameter_service)


@pytest.fixture
def shipment():
    s = mock.Mock()
    s.is_domestic = True
    return s


@pytest.mark.parametrize("phone, expected_phone, setting_default", [
    (None, '07346923435', True),
    ('', '07346923435', True),
    ('0 7  344546234', '07344546234', False),
    ('7 344546234', '07344546234', False),
    ('344546234', '07346923435', True),
    ('+ 44 72453', '072453', False),
    ('0 044 72453', '072453', False),
    ('0 44 72453', '07346923435', True),
    ('+44 072453', '07346923435', True),
    ('+44472453', '07346923435', True),
])
def test_providing_phone_for_domestic_shipment_if_needed(
        phone, expected_phone, setting_default,
        service, get_parameter_service, shipment):
    get_parameter_service.return_value = '07346923435'
    shipment.shipping_address.phone = phone
    assert shipment.is_domestic is True

    service.provide(shipment, 'GB')

    assert shipment.shipping_address.phone == expected_phone
    if setting_default:
        calls = get_parameter_service.call_args_list
        assert calls == [call('default_phone_for_domestic_GB')]


def test_not_providing_phone_for_domestic_shipment_if_no_default_set(
        service, get_parameter_service, shipment):
    get_parameter_service.side_effect = FileNotFoundError
    shipment.shipping_address.phone = None

    service.provide(shipment, 'PL')

    assert shipment.shipping_address.phone is None
    calls = get_parameter_service.call_args_list
    assert calls == [call('default_phone_for_domestic_PL')]
