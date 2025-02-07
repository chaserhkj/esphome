import logging

from esphome import pins
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import (
    CONF_ID,
    CONF_INPUT,
    CONF_INVERTED,
    CONF_MODE,
    CONF_NUMBER,
    CONF_OPEN_DRAIN,
    CONF_OUTPUT,
    CONF_PULLDOWN,
    CONF_PULLUP,
)

from .const import host_ns

_LOGGER = logging.getLogger(__name__)

HostGPIOPin = host_ns.class_("HostGPIOPin", cg.InternalGPIOPin)


def _translate_pin(value):
    if isinstance(value, dict) or value is None:
        raise cv.Invalid(
            "This variable only supports pin numbers, not full pin schemas "
            "(with inverted and mode)."
        )
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise cv.Invalid(f"Invalid pin number: {value}")
    try:
        return int(value)
    except ValueError:
        pass
    if value.startswith("GPIO"):
        return cv.int_(value[len("GPIO") :].strip())
    return value


def validate_gpio_pin(value):
    return _translate_pin(value)


HOST_PIN_SCHEMA = pins.gpio_base_schema(
    HostGPIOPin,
    validate_gpio_pin,
    modes=[CONF_INPUT, CONF_OUTPUT, CONF_OPEN_DRAIN, CONF_PULLUP, CONF_PULLDOWN],
)


@pins.PIN_SCHEMA_REGISTRY.register("host", HOST_PIN_SCHEMA)
async def host_pin_to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    num = config[CONF_NUMBER]
    cg.add(var.set_pin(num))
    cg.add(var.set_inverted(config[CONF_INVERTED]))
    cg.add(var.set_flags(pins.gpio_flags_expr(config[CONF_MODE])))
    return var
