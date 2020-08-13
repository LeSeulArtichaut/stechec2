import textwrap
from functools import partial
from jinja2 import contextfilter

from . import register_filter, register_test


@register_filter
def camel_case(value: str) -> str:
    """Convert a snake case identifier to a upper camel case one"""
    return "".join(i.capitalize() for i in value.split("_"))


@register_test
def is_returning(func) -> bool:
    return func['fct_ret_type'] != 'void'


@register_test
def is_array(type) -> bool:
    return type.endswith(' array')


@register_filter
def get_array_inner(type) -> bool:
    return type[:-len(' array')]


@register_test
def is_tuple(struct) -> bool:
    return struct['str_tuple']


@register_filter
def generic_args(value, type_mapper=lambda x: x) -> str:
    return ", ".join("{} {}".format(type_mapper(type_), name)
                     for [name, type_, _] in value)


@register_filter
def generic_prototype(func, prefix='', type_mapper=lambda x: x,
                      arg_mapper=None) -> str:
    if arg_mapper is None:
        arg_mapper = partial(generic_args, type_mapper=type_mapper)
    return '{} {}{}({})'.format(
        type_mapper(func['fct_ret_type']), prefix, func['fct_name'],
        arg_mapper(func['fct_arg']))


@register_filter
def generic_comment(value: str, start: str, indent: int = 0) -> str:
    newline = "\n" + indent * " " + start
    return start + newline.join(textwrap.wrap(
        value,
        79 - indent - len(start),
        expand_tabs=False,
        break_long_words=False,
        replace_whitespace=False
    ))

@register_filter
def can_fail(func) -> bool:
    return func.get('fct_can_fail', False)

@register_test
@contextfilter
def is_numeric(ctx, value) -> bool:
    """
    Returns whether a type contains only numbers, that is, it is itself a number
    or all its fields 'are numeric' recursively
    """

    if value in ['int', 'double']:
        return True

    as_struct = ctx['game'].get_struct(value)
    if as_struct:
        return all(is_numeric(ctx, field_type) for _, field_type, _ in as_struct['str_field'])

    return False


@register_filter
@contextfilter
def numeric_fields(ctx, struct):
    return [(f_name, f_type, f_doc) for f_name, f_type, f_doc in struct['str_field'] if is_numeric(ctx, f_type)]
