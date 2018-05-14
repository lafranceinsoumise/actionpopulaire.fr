from django.http.response import HttpResponseRedirect

from .models import Payment


def get_payment_response(person, type, price, meta=None):
    """Generate payment response for person with type and price

    :param person: person that is paying, must have all necessary fields (name and location)
    :param type: type of payment
    :param price: price as a decimal
    :param meta: an arbitrary bundle of data that will be sent to the payment provider
    :return: an HTTP response
    """
    if meta is None:
        meta = {}

    person_fields = ['first_name', 'last_name', 'email', 'location_address1', 'location_address2', 'location_zip',
                     'location_state', 'location_city', 'location_country',]

    return HttpResponseRedirect(Payment.objects.create(
        person=person,
        type=type,
        price=price,
        meta=meta,
        **{f: getattr(person, f) for f in person_fields}
    ).get_payment_url())
