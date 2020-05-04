class PhoneProvider:
    def __init__(self, parameters_service):
        self._parameters_service = parameters_service

    def provide(self, shipment, country):
        shipment.shipping_address.phone = \
            self._ensure_phone(shipment.shipping_address.phone, country)
        if not shipment.shipping_address.phone:
            try:
                shipment.shipping_address.phone = self._parameters_service(
                    'default_phone_for_domestic_%s' % country)
            except FileNotFoundError:  # phone won't be provided
                pass

    @staticmethod
    def _ensure_phone(phone, country):
        if not phone:
            return phone
        if country == 'GB':
            phone = "".join(phone.split())
            if not phone.startswith('07'):
                if phone.startswith('+44'):
                    phone = phone[3:]
                elif phone.startswith('0044'):
                    phone = phone[4:]
                if phone.startswith('7'):
                    phone = '0' + phone  # valid
                else:  # invalid
                    return None

        return phone  # valid
