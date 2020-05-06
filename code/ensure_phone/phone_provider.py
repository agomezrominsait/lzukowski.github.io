from typing import Callable, NewType, Optional, Text

Country = NewType('Country', Text)
Phone = NewType('Phone', Text)
ParameterService = Callable[[Text], Text]


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

    def provide(
            self, phone: Optional[Phone], country: Country
    ) -> Optional[Phone]:
        if country != 'GB':
            return phone
        validated_phone = phone and self._get_valid_phone(phone)
        return validated_phone or self._company_support_line()

    @classmethod
    def _get_valid_phone(cls, phone: Phone) -> Optional[Phone]:
        phone = normalize_gb_phone(phone)
        return phone if phone.startswith('07') else None

    def _company_support_line(self) -> Optional[Phone]:
        return Phone(self._get_parameter(f'default_phone_for_domestic_GB'))
