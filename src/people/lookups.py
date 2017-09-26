from ajax_select import register, LookupChannel

from .models import Person

@register('people')
class TagsLookup(LookupChannel):

    model = Person

    def get_query(self, q, request):
        return self.model.objects.filter(email__startswith=q).order_by('email')[:50]

    def format_item_display(self, item):
        return u"<span class='person'>%s (%s)</span>" % (item.get_full_name(), item.email)
