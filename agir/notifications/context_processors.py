from agir.notifications.actions import NotificationRequestManager


def notifications(request):
    """Inclut les annonces dans tous les contextes.

    Le `NotificationRequestManager` est paresseux, les notifications ne sont récupérées que si elles
    sont effectivement utilisées.

    :param request:
    :return:
    """
    return {"notifications": NotificationRequestManager(request)}
