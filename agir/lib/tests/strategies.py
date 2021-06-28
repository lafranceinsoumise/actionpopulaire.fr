import re

from hypothesis import strategies as st
from hypothesis.extra.django import from_model, TestCase as HypothesisTestCase

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


class TestCase(HypothesisTestCase):
    """Classe helper pour faire marcher setUp avec Hypothesis

    Le comportement de `hypothesis.extra.django.TestCase` est en partie cassée par rapport à la façon dont la classe
    Django correspondante fonctionne. En effet, dans les tests Django, on initialise souvent des instances de base de
    données, en comptant sur le fait qu'ils seront détruits automatiquement avant le test suivant par le rollback
    effectué à la fin du test.

    Malheureusement, pour un test hypothesis, `hypothesis.extra.django.TestCase` appelle `setUp`, puise initialise la
    transaction avant chaque exemple (en appelant éventuellement `setup_example` juste après), avec un rollback après
    chaque exemple. Cela signifie que l'effet du `setUp` n'est pas dans la transaction et n'est donc pas rollback.

    Avec cette classe, la méthode `setUp` est appelée au début du test pour les tests django classiques,
    mais non pour les tests hypothesis où elle est appelée au début de chaque exemple à la place.

    Par contre, dans le cas où la classe définit une méthode `setup_example` appelée avant celle définie ci-dessous
    dans l'ordre de résolution, on revient au fonctionnement normal, avec `setUp` appelée au début du test, et
    `setup_example` appelé pour chaque exemple, et il faut dans ce cas être vigilant à ne pas créer d'objets de base de
    données dans le `setUp` sans les détruire explicitement dans le `tearDown`.
    """

    def _should_call_setup_teardown_anyway(self):
        setup_example = getattr(self.__class__, "setup_example")
        return setup_example != TestCase.setup_example

    def _callSetUp(self):
        test_method = getattr(self, self._testMethodName)

        if (
            not getattr(test_method, "is_hypothesis_test", False)
            or self._should_call_setup_teardown_anyway()
        ):
            self.setUp()

    def _callTearDown(self):
        test_method = getattr(self, self._testMethodName)
        if (
            not getattr(test_method, "is_hypothesis_test", False)
            or self._should_call_setup_teardown_anyway()
        ):
            self.tearDown()

    def setup_example(self):
        super().setup_example()
        if not self._should_call_setup_teardown_anyway():
            self.setUp()

    def teardown_example(self, example):
        if not self._should_call_setup_teardown_anyway():
            self.tearDown()
        super().teardown_example(example)
