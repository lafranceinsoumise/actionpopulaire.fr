from crispy_forms.layout import Layout, Submit, Div, Field, MultiField, HTML, Row, Fieldset


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
