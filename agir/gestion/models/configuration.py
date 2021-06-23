import decimal

from agir.gestion.typologies import TypeDepense


class EngagementAutomatique:
    _CLE_CONFIGURATION = "engagement_automatique"

    def __init__(self, compte=None):
        self.compte = compte

    def __get__(self, obj, objtype=None):
        return self.__class__(obj)

    def __contains__(self, item):
        return str(item) in self.compte.configuration.get(self._CLE_CONFIGURATION, {})

    def __getitem__(self, item):
        if item not in TypeDepense:
            raise KeyError(f"{item} n'est pas un type de dépense acceptable")

        # On convertit en chaîne pour le cas où on aurait un objet de type TypeDepense
        item = str(item)

        engagement_automatique = self.compte.configuration.get(
            self._CLE_CONFIGURATION, {}
        )

        if item in engagement_automatique:
            plafond = engagement_automatique[item]

            try:
                return decimal.Decimal(plafond)
            except decimal.DecimalException:
                pass

            # Mieux vaut juste crasher que risque d'engager une dépense incorrectement une dépense,
            # ou même refuser silencieusement l'engagement d'un truc qui devrait être engagé.
            raise RuntimeError(
                f"Valeur de plafond incorrect pour {self.compte!r} pour le type {item!r}"
            )

    def __setitem__(self, key, value):
        if key not in TypeDepense:
            raise KeyError(f"{key} n'est pas un type de dépense acceptable")

        if not isinstance(value, decimal.Decimal):
            raise ValueError(f"{value!r} n'est pas un nombre décimal.")

        # On convertit en chaîne pour le cas où on aurait un objet de type TypeDepense
        key = str(key)
        # La valeur décimale est convertie en str pour garder le même niveau de précision (ce qui ne serait pas le cas
        # en stockant en float)
        value = str(value)

        self.compte.configuration.setdefault(self._CLE_CONFIGURATION, {})[key] = value
