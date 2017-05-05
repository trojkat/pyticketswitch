import pytest
import datetime
from dateutil.tz import tzoffset
from pyticketswitch.mixins import JSONMixin, PaginationMixin, SeatPricingMixin


class TestJSONMixin:

    ZULU = tzoffset('ZULU', 0)

    class Foo(JSONMixin, object):

        def __init__(self, bar):
            self.bar = bar

    def test_with_none(self):
        obj = self.Foo(None)
        result = obj.__jsondict__()
        assert result == {}

    def test_with_empty(self):
        obj = self.Foo([])
        result = obj.__jsondict__()
        assert result == {}

    def test_with_none_with_hide_none_false(self):
        obj = self.Foo(None)
        result = obj.__jsondict__(hide_none=False)
        assert result == {'bar': None}

    def test_with_empty_with_hide_none_false(self):
        obj = self.Foo([])
        result = obj.__jsondict__(hide_none=False)
        assert result == {}

    def test_with_none_with_hide_empty_false(self):
        obj = self.Foo(None)
        result = obj.__jsondict__(hide_empty=False)
        assert result == {}

    def test_with_empty_with_hide_empty_false(self):
        obj = self.Foo([])
        result = obj.__jsondict__(hide_empty=False)
        assert result == {'bar': []}

    def test_normal_object(self):
        obj = self.Foo('hello world!')
        result = obj.__jsondict__()
        assert result == {'bar': 'hello world!'}

    def test_datetime(self):
        date = datetime.datetime(2017, 1, 25, 12, 39, 40, tzinfo=self.ZULU)
        obj = self.Foo(date)
        result = obj.__jsondict__()
        assert result == {'bar': '2017-01-25T12:39:40+00:00'}

    def test_date(self):
        obj = self.Foo(datetime.date(2017, 1, 25))
        result = obj.__jsondict__()
        assert result == {'bar': '2017-01-25'}

    def test_sub_json(self):
        subobj = self.Foo('hello world!')
        obj = self.Foo(subobj)
        result = obj.__jsondict__()
        assert result == {'bar': {'bar': 'hello world!'}}

    def test_list_of_normals(self):
        obj = self.Foo(['hello', 'world!'])
        result = obj.__jsondict__()
        assert result == {'bar': ['hello', 'world!']}

    def test_dict_of_normals(self):
        obj = self.Foo({'first': 'hello', 'second': 'world!'})
        result = obj.__jsondict__()
        assert result == {'bar': {'first': 'hello', 'second': 'world!'}}

    def test_list_of_subobjs(self):
        obj = self.Foo([self.Foo('hello'), self.Foo('world!')])
        result = obj.__jsondict__()
        assert result == {'bar': [{'bar': 'hello'}, {'bar': 'world!'}]}

    def test_dict_of_subobjs(self):
        obj = self.Foo({
            'first': self.Foo('hello'),
            'second': self.Foo('world!')
        })
        result = obj.__jsondict__()
        assert result == {
            'bar': {
                'first': {'bar': 'hello'},
                'second': {'bar': 'world!'}
            }
        }

    def test_as_json(self):
        obj = self.Foo('hello world!')
        result = obj.as_json()
        assert result == '{"bar": "hello world!"}'

    def test_as_dict_for_json(self):
        obj = self.Foo('hello world!')
        result = obj.as_dict_for_json()
        assert result == {'bar': 'hello world!'}


class TestPaginationMixin:

    def test_from_api_data(self):

        data = {
            'results': {
                "paging_status": {
                    "page_length": 50,
                    "page_number": 2,
                    "pages_remaining": 3,
                    "results_remaining": 150,
                    "total_unpaged_results": 250,
                }
            }
        }

        class FakeBaseMeta(object):

            @classmethod
            def from_api_data(cls, data):
                return cls()

        class FakeMeta(PaginationMixin, FakeBaseMeta):
            pass

        meta = FakeMeta.from_api_data(data)

        assert meta.page_length == 50
        assert meta.page_number == 2
        assert meta.pages_remaining == 3
        assert meta.results_remaining == 150
        assert meta.total_results == 250

    def test_is_paginated_pages_remaining(self):
        meta = PaginationMixin(
            page_length=50,
            page_number=1,
            pages_remaining=15,
            total_results=750,
        )

        assert meta.is_paginated() is True

    def test_is_paginated_with_less_results_than_page(self):
        meta = PaginationMixin(
            page_length=50,
            page_number=1,
            pages_remaining=0,
            total_results=30,
        )

        assert meta.is_paginated() is False

    def test_is_paginated_on_last_page(self):
        meta = PaginationMixin(
            page_length=50,
            page_number=15,
            pages_remaining=0,
            total_results=750,
        )

        assert meta.is_paginated() is True

    def test_is_paginated_when_something_is_fucked(self):
        meta = PaginationMixin(
            page_length=None,
            page_number=None,
            pages_remaining=None,
            total_results=None,
        )

        assert meta.is_paginated() is False


class TestSeatPricingMixin:

    def test_kwargs_from_api_data(self):

        data = {
            'sale_seatprice': 160,
            'sale_surcharge': 5.5,
            'non_offer_sale_seatprice': 200,
            'non_offer_sale_surcharge': 5.5,
        }

        kwargs = SeatPricingMixin.kwargs_from_api_data(data)

        assert kwargs['seatprice'] == 160.00
        assert kwargs['surcharge'] == 5.5
        assert kwargs['non_offer_seatprice'] == 200
        assert kwargs['non_offer_surcharge'] == 5.5

    def test_combined_price(self):
        inst = SeatPricingMixin(seatprice=123.45, surcharge=6.78)
        assert inst.combined_price() == 130.23

    def test_combined_price_missing_prices(self):
        inst = SeatPricingMixin(seatprice=123.45)
        with pytest.raises(AssertionError):
            inst.combined_price()

        inst = SeatPricingMixin(surcharge=6.78)
        with pytest.raises(AssertionError):
            inst.combined_price()

    def test_non_offer_combined_price(self):
        inst = SeatPricingMixin(non_offer_seatprice=123.45,
                                non_offer_surcharge=6.78)

        assert inst.non_offer_combined_price() == 130.23

    def test_non_offer_combined_price_missing_prices(self):
        inst = SeatPricingMixin(non_offer_seatprice=123.45)
        with pytest.raises(AssertionError):
            inst.non_offer_combined_price()

        inst = SeatPricingMixin(non_offer_surcharge=6.78)
        with pytest.raises(AssertionError):
            inst.non_offer_combined_price()
