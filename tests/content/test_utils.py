import pytest

from maasaic.apps.content.utils import get_margin_string_from_position
from maasaic.apps.content.utils import get_position_dict_from_margin
from maasaic.apps.content.utils import get_position_string_from_position
from maasaic.apps.content.utils import clean_path


@pytest.mark.parametrize('margin, position', [
    ('10px', {'top': 10, 'right': 10, 'bottom': 10, 'left': 10}),
    ('10px 20px', {'top': 10, 'right': 20, 'bottom': 10, 'left': 20}),
    ('10px 20px 30px', {'top': 10, 'right': 20, 'bottom': 30, 'left': 20}),
    ('10px 20px 30px 40px', {'top': 10, 'right': 20, 'bottom': 30, 'left': 40}),
    ('10px 20px 30px 40px 50px', {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}),
    ('', {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}),
    ('10pxa', {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}),
    ('10px a', {'top': 10, 'right': 10, 'bottom': 10, 'left': 10}),
])
def test_get_position_dict_from_margin(margin, position):
    assert get_position_dict_from_margin(margin) == position


@pytest.mark.parametrize('position, margin', [
    ({'top': 10, 'right': 10, 'bottom': 10, 'left': 10}, 'top: 10px; right: 10px; bottom: 10px; left: 10px;'),
    ({'top': 10, 'right': 20, 'bottom': 30, 'left': 40}, 'top: 10px; right: 20px; bottom: 30px; left: 40px;'),
])
def test_get_position_string_from_dict(position, margin):
    assert get_position_string_from_position(position) == margin


@pytest.mark.parametrize('position, margin', [
    ({'top': 10, 'right': 10, 'bottom': 10, 'left': 10}, '10px'),
    ({'top': 10, 'right': 20, 'bottom': 10, 'left': 20}, '10px 20px'),
    ({'top': 10, 'right': 20, 'bottom': 30, 'left': 20}, '10px 20px 30px'),
    ({'top': 10, 'right': 20, 'bottom': 30, 'left': 40}, '10px 20px 30px 40px'),
    ({'top': 10, 'right': 20, 'bottom': 10, 'left': 40}, '10px 20px 10px 40px'),
])
def test_get_margin_string_from_position(position, margin):
    assert get_margin_string_from_position(position) == margin


@pytest.mark.parametrize('input_str, expected_path', [
    ('', '/'),
    ('/', '/'),
    ('//', '/'),

    ('hello', '/hello'),
    ('/hello/', '/hello'),
    ('hello/', '/hello'),

    ('hello/world', '/hello/world'),
    ('/hello/world/', '/hello/world'),
    ('hello/world/', '/hello/world'),
])
def test_clean_path(input_str, expected_path):
    assert clean_path(input_str) == expected_path

