import pandas as pd
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError as DjangoValidationError


def handle_serializer_exception(val,custom_message="-"):
    if isinstance(val, DjangoValidationError):
        error = next(iter(val.message_dict.values()))[0]
    elif "error" in val.errors:
        error = val.errors["error"][0]
    else:
        key = next(iter(val.errors))
        error = key + ", " + val.errors[key][0]
        error = error.replace("non_field_errors, ", "")

    if custom_message != "-":
        if "unique" in str(error).lower():
            error = custom_message
    return error



def to_decimal(value, default=Decimal("0.00")):
    """
    Universal converter:
    - Handles '5%' -> 0.05
    - Handles '11,250' -> 11250.00
    - Handles None/NaN -> 0.00
    - Handles Int/Float -> Decimal
    """
    # handle None value and NaN
    if pd.isna(value) or value == "":
        return default

    val_str = str(value).strip().replace(',', '')

    is_percentage = False
    if '%' in val_str:
        is_percentage = True
        val_str = val_str.replace('%', '')

    try:
        d_val = Decimal(val_str)
        if is_percentage:
            return d_val / 100
        return d_val
    except InvalidOperation:
        return default


