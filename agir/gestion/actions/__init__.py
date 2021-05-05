import dataclasses
from enum import Enum

from typing import Callable, Union, Any

from django.db import models


class NiveauTodo(Enum):
    IMPERATIF = "imperatif"
    AVERTISSEMENT = "avertissement"
    SUGGESTION = "suggestion"

    def __str__(self):
        return self.value


@dataclasses.dataclass
class Condition:
    condition: Union[Callable[[Any], bool], models.Q]
    message_erreur: str
    niveau_erreur: NiveauTodo

    def check(self, instance):
        if isinstance(self.condition, models.Q):
            return type(instance).objects.filter(self.condition, pk=instance.pk)
        return self.condition(instance)
