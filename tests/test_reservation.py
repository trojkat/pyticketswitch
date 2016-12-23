from pyticketswitch.address import Address
from pyticketswitch.reservation import Reservation
from pyticketswitch.trolley import Trolley


class TestReservation:

    def test_from_api_data(self):

        data = {
            'allowed_countries': {
                'ad': 'Andorra',
                'ae': 'United Arab Emirates',
            },
            'can_edit_address': True,
            'minutes_left_on_reserve': 15,
            'needs_agent_reference': True,
            'needs_email_address': True,
            'needs_payment_card': True,
            'prefilled_address': {
                'address_line_one': 'Metro Building',
                'address_line_two': '1 Butterwick',
                'country_code': 'uk',
                'county': 'United Kingdom',
                'email_address': 'lol@beans.com',
                'home_phone': '020810101010101',
                'postcode': 'W6 8DL',
                'town': 'Hammersmith, London',
                'work_phone': '020801010101010'
            },
            'reserved_trolley': {
                'bundle': [
                    {
                        'bundle_source_code': 'ext_test0',
                        'order': [{'item_number': 1}],
                    }
                ],
                'random_index': '5d3928de-c923-11e6-b2f6-0025903268a0',
                'trolley_bundle_count': 1,
                'trolley_order_count': 1
            },
            "unreserve_orders": [{'item_number': 2}],
        }

        reservation = Reservation.from_api_data(data)

        assert reservation.needs_payment_card is True
        assert reservation.needs_email_address is True
        assert reservation.needs_agent_reference is True
        assert reservation.minutes_left == 15
        assert reservation.can_edit_address is True

        assert isinstance(reservation.prefilled_address, Address)

        assert isinstance(reservation.trolley, Trolley)

        assert len(reservation.allowed_countries) == 2
        assert reservation.allowed_countries[0].code == 'ad'
        assert reservation.allowed_countries[1].code == 'ae'

        assert len(reservation.unreserved_orders) == 1
