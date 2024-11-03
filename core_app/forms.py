import json

from django import forms
from django.forms.widgets import Textarea
from django.utils.safestring import mark_safe

from .models import ExportFile, ParsingLink


class ParsingLinkForm(forms.ModelForm):
    class Meta:
        model = ParsingLink
        fields = '__all__'
        help_texts = {
            'price_formula': mark_safe('You can enter a formula with <code>{{allegro_price}}</code> variable to evaluate your price dynamically based on parsed <code>allegro_price_pln</code> price.'),
            'description_ua': mark_safe('The following system vars will be replaced with parsed values: <code>{{vin}}</code>, <code>{{article}}</code>, <code>{{generation}}</code>, <code>{{translate}}</code>.'),
            'description_ru': mark_safe('The following system vars will be replaced with parsed values: <code>{{vin}}</code>, <code>{{article}}</code>, <code>{{generation}}</code>, <code>{{translate}}</code>.'),
        }


class CustomHeadersTextarea(Textarea):
    template_name = 'admin/core_app/exportfile/custom_headers_textarea.html'


class ExportFileForm(forms.ModelForm):
    class Meta:
        model = ExportFile
        fields = ['file_name', 'schedule_time', 'items_count', 'custom_headers']

    custom_headers = forms.CharField(
        widget=CustomHeadersTextarea,
        required=False
    )

    def clean_custom_headers(self):
        data = self.cleaned_data['custom_headers'].strip()
        data = data.replace("'", '"')
        if not data:
            return {}

        try:
            headers = json.loads(data)
            if not isinstance(headers, dict):
                raise ValueError
        except ValueError:
            raise forms.ValidationError("Invalid JSON format")
        return headers


class ImportProxiesForm(forms.Form):
    file = forms.FileField()
