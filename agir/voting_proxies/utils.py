from agir.lib.http import add_query_params_to_url
from agir.people.models import Person

ISE_URL = "https://www.service-public.fr/particuliers/vosdroits/services-en-ligne-et-formulaires/ISE"


def get_ise_link_for_voting_proxy(voting_proxy):
    params = {}

    if voting_proxy.last_name:
        params["name"] = voting_proxy.last_name
    if voting_proxy.first_name:
        params["firstNames"] = voting_proxy.first_name

    if voting_proxy.person_id:
        if voting_proxy.person.gender == Person.GENDER_FEMALE:
            params["sexe"] = "feminin"
        if voting_proxy.person.gender == Person.GENDER_MALE:
            params["sexe"] = "masculin"

    if voting_proxy.date_of_birth:
        params["birthYear"] = voting_proxy.date_of_birth.year
        params["birthMonth"] = voting_proxy.date_of_birth.month
        params["birthDay"] = voting_proxy.date_of_birth.day

    if voting_proxy.commune_id is not None:
        params["where"] = "france"
    if voting_proxy.consulate_id is not None:
        params["where"] = "world"

    link = add_query_params_to_url(ISE_URL, params)

    return link
