from django import forms
from django_countries import countries


class TagMixin:
    tags = []
    tag_model_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        person_tags = self.instance.tags.all().values_list('label', flat=True)

        for tag, tag_label in self.tags:
            self.fields[tag] = forms.BooleanField(
                label=tag_label,
                required=False,
                initial=tag in person_tags
            )

    def _save_m2m(self):
        """save all tags
        :return:
        """
        super()._save_m2m()

        tags = self.tag_model_class.objects.filter(label__in=[tag for tag, _ in self.tags])

        tags_in = set(tag for tag in tags if self.cleaned_data[tag.label])
        tags_out = set(tag for tag in tags if not self.cleaned_data[tag.label])

        current_tags = set(self.instance.tags.all())

        # all tags that have to be added
        tags_missing = tags_in - current_tags
        if tags_missing:
            self.instance.tags.add(*tags_missing)

        tags_excess = tags_out & current_tags
        if tags_excess:
            self.instance.tags.remove(*tags_excess)


class LocationFormMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['location_country'].choices = countries

        if not self.instance.location_country:
            self.fields['location_country'].initial = 'FR'

    def clean(self):
        """Makes zip code compulsory for French address"""
        cleaned_data = super().clean()

        if cleaned_data['location_country'] == 'FR' and not cleaned_data['location_zip']:
            self.add_error('location_zip', _('Le code postal est obligatoire pour les adresses françaises.'))

        return cleaned_data
