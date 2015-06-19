# Personalized tags and filters for cloud application
from __future__ import division  # Makes integer divisions return float values
import logging
from django import forms
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

# Configure logging for the module name
logger = logging.getLogger(__name__)

AVAILABLE_UNITS = [
    # BYTE_UNITS
    {
        "base_unit": "B",
        "B": {
            "verbose_name": "byte",
            "conversion_value": 1
        },
        "KB": {
            "verbose_name": "kilobyte",
            "conversion_value": 2**10
        },
        "MB": {
            "verbose_name": "megabyte",
            "conversion_value": 2**20
        },
        "GB": {
            "verbose_name": "gigabyte",
            "conversion_value": 2**30
        },
        "TB": {
            "verbose_name": "terabyte",
            "conversion_value": 2**40
        },
        "PB": {
            "verbose_name": "petabyte",
            "conversion_value": 2**50
        },
        "EB": {
            "verbose_name": "exabyte",
            "conversion_value": 2**60
        },
        "ZB": {
            "verbose_name": "zettabyte",
            "conversion_value": 2**70
        },
        "YB": {
            "verbose_name": "yottabyte",
            "conversion_value": 2**80
        }
    }

    # BPS_UNITS
    , {
        "base_unit": "bps",
        "bps": {
            "verbose_name": "bits per second",
            "conversion_value": 1
        },
        "Kbps": {
            "verbose_name": "kilobits per second",
            "conversion_value": 10**3
        },
        "Mbps": {
            "verbose_name": "megabits per second",
            "conversion_value": 10**6
        },
        "Gbps": {
            "verbose_name": "gigabits per second",
            "conversion_value": 10**9
        },
        "Tbps": {
            "verbose_name": "terabits per second",
            "conversion_value": 10**12
        },
        "Pbps": {
            "verbose_name": "petabits per second",
            "conversion_value": 10**15
        },
    }

    # TIME_UNITS
    , {
        "base_unit": "s",
        "ps": {
            "verbose_name": "picosecond",
            "conversion_value": 10**-12
        },
        "ns": {
            "verbose_name": "nanosecond",
            "conversion_value": 10**-9
        },
        "us": {
            "verbose_name": "microsecond",
            "conversion_value": 10**-6
        },
        "ms": {
            "verbose_name": "millisecond",
            "conversion_value": 10**-3
        },
        "s": {
            "verbose_name": "second",
            "conversion_value": 1
        },
        "m": {
            "verbose_name": "minute",
            "conversion_value": 60
        },
        "h": {
            "verbose_name": "hour",
            "conversion_value": 60*60
        }
    },
]

# Decides a good human readable unit based on the dictionary of units and the value to be presented
def human_readable_unit(value, unit, units_dict):
    # Multiply the value with its conversion to get to base unit
    conversion = units_dict[unit]["conversion_value"]
    base_value = value * conversion

    # Try to find a good unit
    best_value = base_value
    best_unit = units_dict["base_unit"]
    for u in units_dict:
        if not type(units_dict[u]) == dict or not units_dict[u].has_key("conversion_value"):
            continue
        # Will try to convert only in one direction
        new_value = base_value / units_dict[u]["conversion_value"]
        if abs(base_value) < 1 and abs(units_dict[u]["conversion_value"]) < 1:
            if new_value > 1 and new_value > best_value:
                best_value = new_value
                best_unit = u
        elif abs(base_value) >= 1 and abs(units_dict[u]["conversion_value"]) >= 1:
            if new_value > 1 and new_value < best_value:
                best_value = new_value
                best_unit = u

    return best_unit

# Performs the conversion from one unit to the other
def do_unit_conversion(value, from_unit, to_unit, units_dict):
    conversion = units_dict[from_unit]["conversion_value"]
    base_value = value * conversion

    return base_value / units_dict[to_unit]["conversion_value"]

# Converts units to human readable values (e.g., 1024 KB -> 1 MB)
@register.filter
def unit_convert(value, arg):

    # More than one conversion parameters can be passed using a comma separated list
    args = arg.split(",")

    # At least one parameter is passed representing the original unit of the value
    from_unit = args[0]
    # By default the output will be formatted (e.g., 1.45 GB)
    formatted_output = True

    # When two parameter are passed the second one represents the unit to convert the value to
    if len(args) > 1:
        to_unit = args[1]
        # When a third parameter is passed this will tell the output style (i.e., number_output or formatted_output [default])
        if len(args) > 2 and args[2] == "number_output":
            formatted_output = False
    else:
        # This means we have to decide a human readable unit to convert to
        to_unit = "*"

    # Input value must be of a numeric type
    if type(value) != long and type(value) != int and type(value) != float:
        if formatted_output:
            return str(value) + " " + from_unit
        else:
            return str(value)

    # Will try to find the unit and how to convert it
    found = False
    for unit in AVAILABLE_UNITS:
        if unit.has_key(from_unit):
            # From and to units must be of the same "type" or in case of "*" will try to guess the best conversion
            if to_unit == "*":
                to_unit = human_readable_unit(value, from_unit, unit)

            if unit.has_key(to_unit):
                value = do_unit_conversion(value, from_unit, to_unit, unit)

            found = True
            # logger.debug("Found! Will convert units (%s -> %s)! " % (from_unit, to_unit))
            break
        # Could not convert so will keep the same unit
    if not found:
        logger.debug("Could not convert so will keep the same unit (%s -> %s)! " % (from_unit, to_unit))
        to_unit = from_unit

    # Formats and returns the value
    if formatted_output:
        if to_unit == "*":
            to_unit = from_unit
        return str(round(value, 2)) + " " + to_unit
    else:
        return str(value)

# Returns the percentage value for the CPU metric given as arg (value should be the whole cpu stats dictionary)
@register.filter
def cpu_stats_percentage(value, arg):
    # Make sure the cpu stats dictionary has the key passed in arg
    if not value.has_key(arg):
        return 0

    total_cpu_time = 0
    for t in value:
        total_cpu_time += value[t]

    if total_cpu_time > 0:
        percent = (value[arg]/total_cpu_time)*100
    else:
        return 0

    return round(percent, 2)

# Abbreviates a string and generates a title with the full content
@register.filter
def abbreviate(value, arg):
    if len(value) > arg:
        abbrev = value[:arg] + "..."
        return mark_safe("<span title='" + conditional_escape(value) + "'>" + conditional_escape(abbrev) + "</span>")
    else:
        return mark_safe(conditional_escape(value))


# To help rendering bootstrap forms (borrowed from https://github.com/tzangms/django-bootstrap-form/)

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_multiple_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_radio(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)
