from operator import itemgetter
from typing import Iterable
from crispy_forms.layout import Layout, Submit, Div, Field, MultiField, HTML, Row, Fieldset, LayoutObject


class FullCol(Div):
    css_class = "col-xs-12"


class HalfCol(Div):
    css_class = "col-xs-12 col-md-6"


class ThirdCol(Div):
    css_class = "col-xs-12 col-md-4"


class FormGroup(Div):
    css_class = "form-group"


def Section(title, *args):
    return Div(
        HTML(f'<h4 class="padtopmore padbottom">{title}</h4>'),
        *args
    )


def remove_excluded_field_from_layout(layout : Layout, excluded_fields : Iterable[str]):
    """Remove excluded fields, and their parents elements, from the layout

    The algorithm is very naïve but works:
    - Get all layout objects in the layout, and sort them lexicographically according to
      the layout object path inside the layout (the path is the sequence of array index
      to get the layout object from the layout
    - for each layout object, determine which fields it contain, by iterating from all fields
      and keeping the fields whose path includes as a prefix the path of the layout object.
      If these fields are all in the `excluded_fields` list, we can safely remove it from the layout

    The sorting in the first step is there to make sure we're removing children before parents,
    and bigger indexes before smaller indexes, so that we don't have to check that a layout object's
    parent has not been removed, or compute an offset for the indexes that account for the objects
    we already deleted.

    In step 2, we have a special case where if the list of fields included in the layout object is
    empty, we do not delete it: this case include html elements with warning text, for example, and
    without this special case, we would delete it every time.
    """
    layout_objects = sorted(layout.get_layout_objects(LayoutObject, greedy=True), key=itemgetter(0), reverse=True)
    fields = layout.get_field_names()
    excluded_fields = set(excluded_fields) & {f[1] for f in fields}

    if not excluded_fields: return

    for pos, _ in layout_objects:
        relevant_fields = set(f[1] for f in fields if f[0][:len(pos)] == pos)
        if relevant_fields and excluded_fields.issuperset(relevant_fields):
            last, *prefix = reversed(pos)
            obj = layout
            while prefix:
                obj = obj[prefix.pop()]
            del obj[last]
