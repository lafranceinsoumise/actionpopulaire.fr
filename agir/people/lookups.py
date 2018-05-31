from ajax_select import register, LookupChannel

from .models import Person


@register('people')
class TagsLookup(LookupChannel):

    model = Person

    def get_query(self, q, request):
        return self.model.objects.filter(emails__address__startswith=q).order_by('emails__address')[:50]

    def format_item_display(self, item):
        return u"<span class='person'>%s (%s)</span>" % (item.get_full_name(), item.email)

    def check_auth(self, request):
        return request.user.has_perm('view_person')

    def get_objects(self, ids):
        # monkey patching of super() method
        pk_type = self.model._meta.pk.to_python

        # Return objects in the same order as passed in here
        ids = [pk_type(pk) for pk in ids]
        things = self.model.objects.in_bulk(ids)
        return [things[aid] for aid in ids if aid in things]
