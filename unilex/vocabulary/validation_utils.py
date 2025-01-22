from decimal import Decimal, InvalidOperation
import string
import json


def validation_simple(value, obj=None):
    """
    Validates that at least one character has been entered.
    Not change is made to the value.
    """
    if len(value) > 1:
        return True, value
    return False, value


def validation_integer(value, obj=None):
    """
    Validates that value is an integer number.
    No change is made to the value
    """
    try:
        int(value)
        return True, value
    except ValueError:
        return False, value


def validation_yesno(value, obj=None):
    """
    Validates that yes or no is entered.
    Converts the yes or no to capitalized version
    """
    if string.upper(value) in ['YES', 'NO']:
        return True, string.capitalize(value)
    return False, value


def validation_decimal(value, obj=None):
    """
    Validates that the number can be converted to a decimal
    """
    try:
        Decimal(value)
        return True, value
    except InvalidOperation:
        return False, value


def validation_json(value, obj=None):
    """Validates that value is valid JSON."""
    try:
        json.loads(value)
        return True, value
    except json.decoder.JSONDecodeError:
        return False, value


def validate_attribute_value(attribute, value, obj):
    """Helper for forms validating values for AttributeOption."""
    function_name = attribute.validation
    validation_function = locals()[function_name]
    return validation_function(value, obj)
