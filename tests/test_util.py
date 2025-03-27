"""Test for Util class"""

from custom_components.teslafi.util import (
    _is_state,
    _is_state_in,
    _lower_or_none,
    _int_or_none,
    _convert_to_bool,
)

def test_is_state():
    """Test _is_state function"""
    assert _is_state("on", "on") is True
    assert _is_state("off", "on") is False
    assert _is_state(None, "on") is None
    assert _is_state("off", None) is False
    assert _is_state(None, None) is None
    
def test_is_state_in():
    """Test _is_state_in function"""
    assert _is_state_in("on", ["on", "off"]) is True
    assert _is_state_in("off", ["on", "off"]) is True
    assert _is_state_in("on", ["off"]) is False
    assert _is_state_in(None, ["on", "off"]) is None
    # assert _is_state_in("off", None) is False
    
def test_lower_or_none():
    """Test _lower_or_none function"""
    assert _lower_or_none("TEST") == "test"
    assert _lower_or_none(None) is None
    assert _lower_or_none("test") == "test"
    
def test_int_or_none():
    """Test _int_or_none function"""
    assert _int_or_none("1") == 1
    assert _int_or_none(None) is None
    assert _int_or_none("0") == 0
    assert _int_or_none("1.5") == 1
    assert _int_or_none("1.9") == 1
    
def test_convert_to_bool():
    """Test _convert_to_bool function"""
    assert _convert_to_bool(True) is True
    assert _convert_to_bool(False) is False
    assert _convert_to_bool(None) is None
    assert _convert_to_bool("0") is False
    assert _convert_to_bool("1") is True
    assert _convert_to_bool("test") is True
    assert _convert_to_bool("") is False
    
    # TODO: Do we want this scenarios to actually eval as true?
    assert _convert_to_bool("False") is True
    assert _convert_to_bool("false") is True
