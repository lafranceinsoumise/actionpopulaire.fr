import re

from hypothesis import strategies as st
from hypothesis.extra.django import from_model, TestCase as HypothesisTestCase

from agir.authentication.models import Role
from agir.people.models import Person


def printable_text(**kwargs):
    return st.text(st.characters(whitelist_categories=["L", "P", "Zs"]), **kwargs)


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
    """Classe helper qui permet d'utiliser tests classiques et tests hypothesis dans le même TestCase

    Avec `hypothesis.extra.django.TestCase`, il n'est pas aisé de mélanger des tests hypothesis et des tests
    "classiques" qui ne font pas usage d'hypothesis.

    En effet, dans les tests Django classiques, on initialise souvent des instances de base de données, en comptant sur
    le fait qu'ils seront détruits automatiquement avant le test suivant par le rollback effectué à la fin du test.

    Or hypothesis ajoute un mécanisme supplémentaire de set up et de tear down : `setup_example`, et `teardown_example`
    qui s'exécutent pour chaque exemple, tandis que `setUp` et `tearDown` s'exécutent une fois pour chaque test,
    indépendamment du nombre d'exemples. Pour garder le système de transactions fonctionnel, hypothesis déplace la
    création et le rollback de la transaction avant et après chaque exemple, et non plus avant et après chaque test. Ce
    sont donc les instances de modèle créées dans `setup_example` qui sont automatiquement rollback, et non celles
    créées dans `setUp`.

    Cela crée donc un problème pour les TestCase mixtes : les instances de modèles créées dans `setUp` seront
    automatiquement rollback dans les tests classiques… mais pas dans les tests hypothesis, et il n'y a donc pas de
    solution évidente pour écrire une fonction de `setUp` commune aux deux types de tests.

    Avec cette classe, la méthode `setUp` est appelée au début du test pour les tests django classiques,
    mais non pour les tests hypothesis où elle est appelée au début de chaque exemple à la place, ce qui permet de
    définir seulement `setUp` et d'avoir le même comportement de rollback pour les deux types de test.

    Par contre, dans le cas où la classe définit une méthode `setup_example`, on revient au fonctionnement normal pour
    un test hypothesis :
    - `setUp` est appelée au début du test, hors de la transaction
    - `setup_example` est appelée pour chaque exemple

    Il faut dans ce cas être vigilant à ne pas créer d'objets de base de données dans le `setUp` sans les détruire
    explicitement dans le `tearDown`.
    """

    def _should_call_setup_teardown_each_example(self):
        setup_example = getattr(self.__class__, "setup_example")

        # Si `setup_example` a été redéfini pour la classe TestCase concrète,
        return setup_example == TestCase.setup_example

    def _callSetUp(self):
        test_method = getattr(self, self._testMethodName)

        if (
            not getattr(test_method, "is_hypothesis_test", False)
            or not self._should_call_setup_teardown_each_example()
        ):
            self.setUp()

    def _callTearDown(self):
        test_method = getattr(self, self._testMethodName)
        if (
            not getattr(test_method, "is_hypothesis_test", False)
            or not self._should_call_setup_teardown_each_example()
        ):
            self.tearDown()

    def setup_example(self):
        super().setup_example()
        if self._should_call_setup_teardown_each_example():
            self.setUp()

    def teardown_example(self, example):
        if self._should_call_setup_teardown_each_example():
            self.tearDown()
        super().teardown_example(example)
