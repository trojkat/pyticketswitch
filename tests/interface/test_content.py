from pyticketswitch.interface.content import Content


class TestContent:

    def test_from_api_data(self):

        data = {
            'name': 'name',
            'value': 'value',
            'value_html': '<p>value</p>',
        }
        content = Content.from_api_data(data, event)
        assert content.name == 'name'
        assert content.value == 'value'
        assert content.value_html == '<p>value</p>'
