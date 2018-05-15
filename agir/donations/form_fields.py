from django import forms
from django.forms.widgets import Input
from webpack_loader.utils import get_files

class AmountWidget(Input):
    input_type = 'hidden'
    is_hidden = False

    @property
    def media(self):
        return forms.Media(js=[script['url'] for script in get_files('donations/amountWidget', 'js')])
