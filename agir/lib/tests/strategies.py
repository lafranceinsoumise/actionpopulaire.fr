import re

from hypothesis import strategies as st
from hypothesis.extra.django import from_model

from agir.authentication.models import Role
from agir.people.models import Person

printable_text = st.text(st.characters(whitelist_categories=["L", "P", "Zs"]))


def no_whitespace_re(s):
    return re.compile(re.sub("\s+", "", s), re.ASCII)


def to_strategy(s):
    if isinstance(s, st.SearchStrategy):
        return s
    return st.just(s)


# les regex sont issues de https://github.com/google/libphonenumber/blob/master/resources/PhoneNumberMetadata.xml
french_mobile_number = st.from_regex(
    no_whitespace_re(
        r"""
\A
  \+33
  (?:
    6(?:
      [0-24-8]\d|
      3[0-8]|
      9[589]
    )|
    7(?:
      00|
      [3-9]\d
    )
  )
  \d{6}
\Z
"""
    )
)

french_landline_number = st.from_regex(
    no_whitespace_re(
        r"""
\A
  \+33
  (?:
    [1-35]\d |
    4[1-9]
  )
  \d{7}
\Z
"""
    )
)


french_phone_number = st.one_of(french_mobile_number, french_landline_number)


@st.composite
def person_with_role(draw, **kwargs):
    defaults = {
        "contact_phone": french_phone_number,
        "image": None,
        "role__is_active": True,
        "role__is_staff": False,
        "role__is_superuser": False,
        "role__type": Role.PERSON_ROLE,
    }

    kwargs = {**defaults, **kwargs}

    email = to_strategy(kwargs.pop("email", st.emails()))
    role_kwargs = {
        k[len("role__") :]: to_strategy(kwargs.pop(k))
        for k in list(kwargs)
        if k.startswith("role__")
    }
    person_kwargs = {k: to_strategy(v) for k, v in kwargs.items()}

    r = draw(from_model(Role, **role_kwargs))
    p = draw(from_model(Person, role=st.just(r), **person_kwargs))
    e = draw(email)
    p.add_email(e, primary=True)

    return p
