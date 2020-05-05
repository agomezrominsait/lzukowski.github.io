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

    valid_gb_phone = no_whitespaces.startswith('07')
    if valid_gb_phone:
        return Phone(no_whitespaces)

    without_country_prefix = no_whitespaces
    if no_whitespaces.startswith('+44'):
        without_country_prefix = no_whitespaces[3:]
    elif no_whitespaces.startswith('0044'):
        without_country_prefix = no_whitespaces[4:]

    if without_country_prefix.startswith('7'):
        return Phone('0' + without_country_prefix)
    else:
        return None


class PhoneProvider:
    def __init__(self, parameters_service: ParameterService):
        self._parameters_service = parameters_service

    def provide(self, shipment: Shipment, country: Country) -> None:
        shipment.shipping_address.phone = \
            self._ensure_phone(shipment.shipping_address.phone, country)
        if not shipment.shipping_address.phone:
            try:
                shipment.shipping_address.phone = self._parameters_service(
                    'default_phone_for_domestic_%s' % country)
            except FileNotFoundError:  # phone won't be provided
                pass

    @staticmethod
    def _ensure_phone(
            phone: Optional[Phone], country: Country,
    ) -> Optional[Phone]:
        if not phone:
            return phone
        if country == 'GB':
            phone = normalize_gb_phone(phone)
        return phone
