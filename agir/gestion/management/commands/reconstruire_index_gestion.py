from django.contrib.admin.options import get_content_type_for_model
from django.core.management import BaseCommand

from agir.gestion.models import InstanceCherchable
from agir.gestion.models.common import SearchableModel


class Command(BaseCommand):
    def handle(self, *args, **options):
        InstanceCherchable.objects.all().delete()

        for model in SearchableModel.__subclasses__():
            ct = get_content_type_for_model(model)
            search_vector = model.search_vector()
            base_sv_qs = model.objects.values(v=search_vector)
            base_num_qs = model.objects.values("numero")

            all_pks = model.objects.values_list("pk", flat=True)

            InstanceCherchable.objects.bulk_create(
                InstanceCherchable(
                    content_type=ct,
                    object_id=pk,
                    recherche=base_sv_qs.filter(pk=pk),
                    numero=base_num_qs.filter(pk=pk),
                )
                for pk in all_pks
            )
