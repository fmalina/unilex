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
    if string.upper(value) in ["YES", "NO"]:
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
    """
    Helper function for forms that wish to validation a value for an
    AttributeOption.
    """
    function_name = attribute.validation.split('.')[-1]
    import_name = '.'.join(attribute.validation.split('.')[:-1])

    # The below __import__() call is from python docs, and is equivalent to:
    #
    #   from import_name import function_name
    #
    import_module = __import__(import_name, globals(), locals(), [function_name])

    validation_function = getattr(import_module, function_name)
    return validation_function(value, obj)
