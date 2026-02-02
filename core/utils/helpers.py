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
