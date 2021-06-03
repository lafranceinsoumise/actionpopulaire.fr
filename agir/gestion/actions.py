import dataclasses
from enum import Enum
from typing import (
    Callable,
    ClassVar,
    Generic,
    List,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from django.db import models
from django.db.models import Manager

from agir.authentication.models import Role


class NiveauTodo(Enum):
    IMPERATIF = "imperatif"
    AVERTISSEMENT = "avertissement"
    SUGGESTION = "suggestion"

    def __str__(self):
        return self.value


class GestionModel(Protocol):
    Etat: ClassVar[Type[Enum]]

    commentaires: Manager

    def todos(self) -> List[Tuple[str, List[Tuple[str, NiveauTodo]]]]:
        return []


T = TypeVar("T", bound=GestionModel)
E = TypeVar("E", bound=Enum)


@dataclasses.dataclass
class Todo(Generic[T]):
    condition: Union[Callable[[T], bool], models.Q]
    message_erreur: str
    niveau_erreur: NiveauTodo

    def check(self, instance):
        if isinstance(self.condition, models.Q):
            return type(instance).objects.filter(self.condition, pk=instance.pk)
        return self.condition(instance)


def toujours(_: T) -> bool:
    return True


# pas besoin d'explication puisque renvoie toujours True
toujours.explication = ""


def no_todos(instance: T) -> bool:
    return not instance.todos() and not instance.commentaires.filter()


no_todos.explication = "Vous devez d'abord terminer la liste de tâches"


@dataclasses.dataclass
class Transition(Generic[T, E]):
    nom: str
    vers: E
    condition: Callable[[T], bool] = toujours
    class_name: str = ""
    permissions: List[str] = dataclasses.field(default_factory=list)

    def refus(self, instance: T, role: Role):
        if all(
            not role.has_perm(p) and not role.has_perm(p, obj=instance)
            for p in self.permissions
        ):
            return "Vous n'avez pas les permissions requises pour cette action."

        if not self.condition(instance):
            # noinspection PyUnresolvedReferences
            return self.condition.explication

        return None
