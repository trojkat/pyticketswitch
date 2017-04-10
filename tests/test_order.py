from pyticketswitch.event import Event
from pyticketswitch.performance import Performance
from pyticketswitch.order import TicketOrder, Order
from pyticketswitch.seat import Seat


class TestTicketOrder:

    def test_from_api_data(self):
        data = {
            'discount_code': 'ADULT',
            'discount_desc': 'Adult standard',
            'no_of_seats': 2,
            'sale_seatprice': 25,
            'sale_surcharge': 2.50,
            'total_sale_seatprice': 50,
            'total_sale_surcharge': 5,
            'seats': [
                {'full_id': 'ABC123'},
                {'full_id': 'DEF456'},
            ]
        }

        ticket_order = TicketOrder.from_api_data(data)

        assert ticket_order.code == 'ADULT'
        assert ticket_order.number_of_seats == 2
        assert ticket_order.description == 'Adult standard'
        assert isinstance(ticket_order.seatprice, float)
        assert ticket_order.seatprice == 25.0
        assert isinstance(ticket_order.surcharge, float)
        assert ticket_order.surcharge == 2.5
        assert isinstance(ticket_order.total_seatprice, float)
        assert ticket_order.total_seatprice == 50.0
        assert isinstance(ticket_order.total_surcharge, float)
        assert ticket_order.total_surcharge == 5.0
        assert len(ticket_order.seats) == 2
        assert ticket_order.seats[0].id == 'ABC123'
        assert ticket_order.seats[1].id == 'DEF456'

    def test_repr(self):
        ticket_order = TicketOrder('abc123')
        assert repr(ticket_order) == '<TicketOrder abc123>'

    def test_combined_price(self):
        data = {
            'discount_code': 'ADULT',
            'discount_desc': 'Adult standard',
            'no_of_seats': 2,
            'sale_seatprice': 25,
            'sale_surcharge': 2.50,
            'total_sale_seatprice': 50,
            'total_sale_surcharge': 5,
            'seats': [
                {'full_id': 'ABC123'},
                {'full_id': 'DEF456'},
            ]
        }
        ticket_order = TicketOrder.from_api_data(data)
        assert ticket_order.combined_price() == 27.50

    def test_total_combined_price(self):
        data = {
            'discount_code': 'ADULT',
            'discount_desc': 'Adult standard',
            'no_of_seats': 2,
            'sale_seatprice': 25,
            'sale_surcharge': 2.50,
            'total_sale_seatprice': 50,
            'total_sale_surcharge': 5,
            'seats': [
                {'full_id': 'ABC123'},
                {'full_id': 'DEF456'},
            ]
        }
        ticket_order = TicketOrder.from_api_data(data)
        assert ticket_order.total_combined_price() == 55.0


class TestOrder:

    def test_from_api_data(self):

        data = {
            "backend_purchase_reference": 'GHI098',
            "event": {
                "event_id": "6IF",
            },
            "item_number": 1,
            "performance": {
                "perf_id": "6IF-A7N",
            },
            "price_band_code": "C/pool",
            "got_requested_seats": True,
            "ticket_orders": {
                "ticket_order": [
                    {"discount_code": "ADULT"},
                    {"discount_code": "CHILD"},
                ]
            },
            "ticket_type_code": "CIRCLE",
            "ticket_type_desc": "Upper circle",
            "total_no_of_seats": 3,
            "total_sale_seatprice": 51,
            "total_sale_surcharge": 5.40,
            "requested_seats": [
                {'full_id': 'ABC123'},
                {'full_id': 'DEF456'},
            ],
            'send_method': {
                'send_code': 'POST',
                'send_cost': 3.5,
                'send_desc': 'Post (UK & Ireland only)',
                'send_type': 'post',
                'permitted_countries': {
                    'country': [
                        {
                            'country_code': 'ie',
                            'country_desc': 'Ireland'
                        },
                        {
                            'country_code': 'uk',
                            'country_desc': 'United Kingdom'
                        }
                    ]
                }
            }
        }

        order = Order.from_api_data(data)

        assert order.item == 1
        assert order.price_band_code == 'C/pool'
        assert order.ticket_type_code == 'CIRCLE'
        assert order.ticket_type_description == 'Upper circle'
        assert order.number_of_seats == 3
        assert order.total_seatprice == 51
        assert order.total_surcharge == 5.40
        assert order.got_requested_seats is True
        assert order.backend_purchase_reference == 'GHI098'

        assert isinstance(order.event, Event)
        assert order.event.id == '6IF'
        assert isinstance(order.performance, Performance)
        assert order.performance.id == '6IF-A7N'

        assert len(order.ticket_orders) == 2
        assert order.ticket_orders[0].code == 'ADULT'
        assert order.ticket_orders[1].code == 'CHILD'

        assert len(order.requested_seats) == 2
        assert order.requested_seats[0].id == 'ABC123'
        assert order.requested_seats[1].id == 'DEF456'

        assert order.total_including_send_cost() == (51 + 5.40 + 3.5)

    def test_from_api_data_with_send_method(self):

        data = {
            'item_number': 1,
            "send_method": {
                "send_code": "COBO",
            },
        }

        order = Order.from_api_data(data)

        assert order.send_method.code == 'COBO'

    def test_get_seats(self):
        ticket_order_one = TicketOrder('a', seats=[
            Seat('A1'), Seat('A2'), Seat('A3'),
        ])

        ticket_order_two = TicketOrder('b', seats=[
            Seat('B1'), Seat('B2'), Seat('B3'),
        ])

        order = Order(1, ticket_orders=[ticket_order_one, ticket_order_two])

        seats = order.get_seats()
        assert [seat.id for seat in seats] == [
            'A1', 'A2', 'A3', 'B1', 'B2', 'B3',
        ]

    def test_get_seat_ids(self):
        ticket_order_one = TicketOrder('a', seats=[
            Seat('A1'), Seat('A2'), Seat('A3'),
        ])

        ticket_order_two = TicketOrder('b', seats=[
            Seat('B1'), Seat('B2'), Seat('B3'),
        ])

        order = Order(1, ticket_orders=[ticket_order_one, ticket_order_two])

        seat_ids = order.get_seat_ids()
        assert seat_ids == ['A1', 'A2', 'A3', 'B1', 'B2', 'B3']

    def test_unique_seat_text(self):
        ticket_order_one = TicketOrder('a', seats=[
            Seat('A1', seat_text='Hell bad'), Seat('A2'), Seat('A3'),
        ])

        ticket_order_two = TicketOrder('b', seats=[
            Seat('B1', seat_text='Hell good'), Seat('B2'), Seat('B3'),
        ])

        order = Order(1, ticket_orders=[ticket_order_one, ticket_order_two])

        seat_text = order.unique_seat_text()
        assert seat_text == 'Hell bad, Hell good'

    def test_get_seats_with_no_ticket_orders(self):
        order = Order(1, ticket_orders=[])
        assert order.get_seats() == []

    def test_get_requested_seat_ids(self):
        order = Order(1, requested_seats=[Seat('A1'), Seat('A2'), Seat('A3')])
        assert order.get_requested_seat_ids() == ['A1', 'A2', 'A3']

    def test_repr(self):
        order = Order(1, ticket_orders=[])
        assert repr(order) == '<Order 1>'
