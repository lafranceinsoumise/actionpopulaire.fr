from django import forms
from django.utils.translation import ugettext as _
from django_countries import countries

__all__ = ['TagMixin', 'LocationFormMixin', 'ContactFormMixin']


class TagMixin:
    tags = []
    tag_model_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        active_tags = [tag.label for tag in self.instance.tags.filter(label__in=[tag for tag, tag_label in self.tags])]

        for tag, tag_label in self.tags:
            self.fields[tag] = forms.BooleanField(
                label=tag_label,
                required=False,
                initial=tag in active_tags
            )

    def _save_m2m(self):
        """save all tags
        :return:
        """
        super()._save_m2m()

        tags = list(self.tag_model_class.objects.filter(label__in=[tag for tag, _ in self.tags]))
        tags_to_create = [self.tag_model_class(label=tag_label)
                          for tag_label, _ in self.tags
                          if tag_label not in {tag.label for tag in tags}]

        if tags_to_create:
            # PostgreSQL only will set the id on original objects
            self.tag_model_class.objects.bulk_create(tags_to_create)

        tags += tags_to_create

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


class LocationFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in ['location_name', 'location_address1', 'location_city', 'location_country']:
            if f in self.fields:
                self.fields[f].required = True

        self.fields['location_country'].choices = countries

        self.fields['location_address1'].label = _('Adresse')
        self.fields['location_address2'].label = False

        if not self.instance.location_country:
            self.fields['location_country'].initial = 'FR'

    def clean(self):
        """Makes zip code compulsory for French address"""
        cleaned_data = super().clean()

        if 'location_country' in cleaned_data and cleaned_data['location_country'] == 'FR' and not cleaned_data['location_zip']:
            self.add_error('location_zip', _('Le code postal est obligatoire pour les adresses françaises.'))

        return cleaned_data


class ContactFormMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['contact_name'].required = True
        self.fields['contact_email'].required = True
        self.fields['contact_phone'].required = True
