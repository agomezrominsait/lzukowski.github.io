from typing import Callable, NewType, Optional, Text

Country = NewType('Country', Text)
Phone = NewType('Phone', Text)
ParameterService = Callable[[Text], Text]


class Shipment:
    class Address:
        phone: Optional[Phone]

    is_domestic: bool
    shipping_address: Address


def normalize_gb_phone(phone: Phone) -> Optional[Phone]:
    no_whitespaces = "".join(phone.split())

    without_country_prefix = no_whitespaces
    if no_whitespaces.startswith('+44'):
        without_country_prefix = f'0{no_whitespaces[3:]}'
    elif no_whitespaces.startswith('0044'):
        without_country_prefix = f'0{no_whitespaces[4:]}'
    elif no_whitespaces.startswith('7'):
        without_country_prefix = f'0{no_whitespaces}'
    return Phone(without_country_prefix)


class PhoneProvider:
    def __init__(self, parameters_service: ParameterService):
        self._get_parameter = parameters_service

    def provide(self, shipment: Shipment, country: Country) -> None:
        phone = shipment.shipping_address.phone
        phone = phone and self._get_valid_phone(phone, country)
        shipment.shipping_address.phone = (
            phone or self._get_default_country_phone(country)
        )

    @staticmethod
    def _get_valid_phone(phone: Phone, country: Country) -> Optional[Phone]:
        if country == 'GB':
            phone = normalize_gb_phone(phone)
            return phone if phone.startswith('07') else None
        return phone

    def _get_default_country_phone(self, country: Country) -> Optional[Phone]:
        try:
            return Phone(
                self._get_parameter(f'default_phone_for_domestic_{country}')
            )
        except FileNotFoundError:
            return None
