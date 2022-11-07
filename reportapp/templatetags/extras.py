from django import template

register = template.Library()


@register.filter
def percent(num: float) -> float:
    return float("{:.2f}".format(num * 100))


@register.filter
def numeric(num: int) -> float:
    return float("{:.2f}".format(num))


@register.filter
def first_name(fio: str) -> str:
    return fio.split(" ")[0]
