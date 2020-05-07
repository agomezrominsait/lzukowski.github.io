---
layout: post
title: Refactoring exercise of some legacy code
categories: [refactoring, legacy]
tags: [python, legacy, refactoring]
---

So there is this legacy code.

It's a good example of code that is pretty simple code but at the same time, hard to understand the business case.
These code snippets are already simplified cause it was a part of a bigger object that was processing shipping order. 

My goal is to refactor it a little and get more knowledge about this part. This is a pretty small code so it's good for practice.

# Original code
These are code snippets. Read it. Note what you discovered. And then we will see if knowledge gathered with refactoring will be the same. I will be refactoring it and describing my steps at the same time so we will see how it will go.

{% highlight python %}
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
{% endhighlight %}

{% highlight python %}
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
    (None, '07341873532', True),
    ('', '07341873532', True),
    ('0 7  344871572', '07344871572', False),
    ('7 344871572', '07344871572', False),
    ('344871572', '07341873532', True),
    ('+ 44 71572', '071572', False),
    ('0 044 71572', '071572', False),
    ('0 44 71572', '07341873532', True),
    ('+44 071572', '07341873532', True),
    ('+44471572', '07341873532', True),
])
def test_providing_phone_for_domestic_shipment_if_needed(
        phone, expected_phone, setting_default,
        service, get_parameter_service, shipment):
    get_parameter_service.return_value = '07341873532'
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
{% endhighlight %}

# Strategy
I want to figure out what is going so for me start point is refactoring test. Probably I will split tests into more specific ones. Then when I will have more knowledge about cases I will refactor code to be more readable, but I don't want to change the general architecture of this code or tests (at least not now).

# Step 1 - tests refactoring

Split test with 'if' statement into two tests. [<a href="{{ site.github.repository_url }}/commit/85235c40fb1227f98671f007794693c223f49cae">commit</a>]

One of the tests is heavily parametrized with one of the arguments being boolean. I decided to split it into two.

Cases with value `True` have the same expected value. [<a href="{{ site.github.repository_url }}/commit/8f780ac7d006bc441da128cd2a3e40d00d93a310">commit</a>]

After splitting cases I see that one of them has the same parametrized value. So I simplified it and put it directly into code.

Parameter service as Dummy instead of Mock [<a href="{{ site.github.repository_url }}/commit/9b412c07caa1a7bf7da162dc34132f359418610e">commit</a>]
I see that Parameter service is Key/Value storage and in every test. Key is `default_phone_for_domestic_{country}` so it's about some default phone for some cases. I decided to prepare `DummyProviderService` with this case (in all tests it's GB with the same phone).

GB is a special case
{% highlight python %}
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
{% endhighlight %}
   * When I looked at code I see that most of the logic is for GB only. You can see it in this fragment. Also from 'comments', we can see that we validating the phone.
   * There is a validating part but also normalizing. Phone number removes country prefix and validation checks if it starts with '07' in GB case
   * So I need to check what is so special for '07' prefix. I google `Great Britain phone 07 prefixes` and I go to <a href="https://en.wikipedia.org/wiki/Telephone_numbers_in_the_United_Kingdom">Wikipedia</a>
   * 07xxxxxxxxx is a prefix for mobile phones, pagers and personal numbering (PNS)
   * I guess that meant to be personal or mobile phone in GB

To be more precise in tests I changed the case for not changing phone number when it's not GB [<a href="{{ site.github.repository_url }}/commit/fb7a05c962a55198fc75422ea553f1be8b4baeaf">commit</a>]
Original tests checked the only situation when phone was `None`. I added more cases and It passed so my assumptions were right.

Change not providing GB phone to check normalization of phone [<a href="{{ site.github.repository_url }}/commit/9decc3c59fe21ffb600ed6cd2bcb6402676a7d83">commit</a>]
So based on what I know, I decided
 *  to split the test into the normalization of phone numbers and tests providing phone.
 * phones with `07` prefix are valid for GB (mobile / personal phone) so I renamed tests so specify valid and invalid cases.  

# Step 2 - code refactoring
So after gathering some knowledge about this functionality, I decided to change a little code and see what I will learn from it. I don't want to change the architecture of this code cause I still may have wrong assumptions.

Some little steps:
 * introduce type annotations [<a href="{{ site.github.repository_url }}/commit/6ac7f235ac6c47c1ac8831ff24aa14f585c4aa19">commit</a>]
 * use Type aliases for Country and Phone [<a href="{{ site.github.repository_url }}/commit/6ac7f235ac6c47c1ac8831ff24aa14f585c4aa19">commit</a>]
 * extract normalization to separate method [<a href="{{ site.github.repository_url }}/commit/d9448a614b37822e3226104cda086646d70e15da">commit</a>]

So this if statements (very ugly) are the main part of the functionality. So I want now refactor them step by step to discover intentions.

 * First I want to start with describing steps with variable names (now phone is just replaced in every step. [<a href="{{ site.github.repository_url }}/commit/80bc9f5526f396d558d544ff13761b0f0f2abea5">commit</a>]

 * I found out that at start and end I'm replacing the prefix of the phone.  Our 07 prefix is valid for number without country code but for when we have country prefix it's without 0 (+447xxxxxxxxx) so when removing prefix we should add 0 for GB. In my mind, I wanted to split normalization to separate class to remove country prefix and spaces. But If I would do this it would be hard to implement this case. That's why I don't like to jump into conclusions too soon case I can miss some strange cases.
 * Now I can split normalization form validation at this point (it's only for GB case) [<a href="{{ site.github.repository_url }}/commit/b72ff455f6164df1c9d6300f7138b0841fa1049c">commit</a>]
 * I don't like that we are passing Optional[Phone] to functions. So the next step is to remove Null as soon as possible and limit if statements. [<a href="{{ site.github.repository_url }}/commit/baabc883e1a2cd7b6c69be0693814bcef2c8a65e">commit</a>]
 * We are passing whole Shipment object to this functionality and replacing the phone inside. I don't want to change architecture, but at least I will change API to receive a phone and return a valid phone. This step simplifies tests also.
 [<a href="{{ site.github.repository_url }}/commit/875939e380f37788acec92c688ccdf9c3d75e1c6">commit</a>] [<a href="{{ site.github.repository_url }}/commit/4b8e10470e93449c97235ec5c753627549e31db1">commit</a>]

# Step 3 - Getting some extra knowledge from the company
At this point, I think I know where and what questions to ask in the company to validate my assumptions.

Base what I found out till know:
  * I guess it's the feature for GB only or GB mainly
  * It's about providing some default phone for shipping courier when given in shipment is invalid
 * I need to ask someone from shipping operations team about this
 * To ask them I've read the value of this GB default phone cause for sure they should know this phone number.

So with this information, they knew about what case this feature is related to. Shipping carriers that we worked within GB requires a personal contact phone in case there will be trouble with delivery.
So operations have a support phone line that will help with cases that the buyer phone was not added to order. They will know more about shipments and will help with delivery in case of problems.

So now I know the context of this functionality. I can specify it more in code and tests. Perfect would be BDD test with gherkin cases and User Story at top of the feature file. But this not goal of this exercise.

# Step 4 - Putting extra knowledge to code and tests
So at the last step, I change tests and code to use explicate `support line` names. 
The next steps would be to change the architecture of this functionality a little and make BDD tests to have more cases described. But it's already better. I will leave it like this for now.

{% highlight python %}
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
{% endhighlight %}

{% highlight python %}
@fixture
def company_support_line():
    return Phone('07346923435')


@fixture
def service(company_support_line):
    def get_parameter(key: Text) -> Text:
        if key != f'default_phone_for_domestic_GB':
            raise FileNotFoundError(key)
        return company_support_line

    return PhoneProvider(get_parameter)


class TestPhoneProvider:
    @mark.parametrize("invalid_phone", [
        None,
        Phone(''),
        Phone('344546234'),
        Phone('0 44 72453'),
        Phone('+44 072453'),
        Phone('+44472453'),
    ])
    def test_company_support_phone_when_when_invalid_phone_in_gb_shipment(
            self, invalid_phone, service, company_support_line,
    ):
        assert service.provide(invalid_phone, Country('GB')) == (
            company_support_line
        )

    @mark.parametrize("valid_phone", [
        Phone('07344546234'),
        Phone('072453'),
    ])
    def test_shipment_phone_when_phone_is_valid_gb_personal_phone(
            self, valid_phone, service,
    ):
        assert service.provide(valid_phone, Country('GB')) == valid_phone

    @mark.parametrize("phone, country", [
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
    @mark.parametrize("phone, normalized_phone", [
        (Phone('0 7  344546234'), '07344546234'),
        (Phone('7 344546234'), '07344546234'),
    ])
    def test_number_normalization_when_valid_gb_phone(
            self, phone, normalized_phone, service,
    ):
        assert service.provide(phone, Country('GB')) == normalized_phone

    @mark.parametrize("phone, normalized_phone", [
        (Phone('+ 44 72453'), '072453'),
        (Phone('0 044 72453'), '072453'),
    ])
    def test_remove_country_prefix_when_valid_gb_phone(
            self, phone, normalized_phone, service,
    ):
        assert service.provide(phone, Country('GB')) == normalized_phone
{% endhighlight %}
