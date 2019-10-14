from django.contrib import messages


def add_message(backend, user, details, new_association, *args, **kwargs):
    request = backend.strategy.request
    email = details.get("email")

    if request is not None:
        if user:
            if new_association:
                messages.add_message(
                    request=request,
                    level=messages.SUCCESS,
                    message=f"Votre compte Facebook a bien été relié à votre compte la France insoumise via votre adresse email {email}",
                )
        else:
            messages.add_message(
                request=request,
                level=messages.ERROR,
                message=f"Vous n'avez pas de compte sur la France insoumise associé à l'adresse email {email}."
                f" Vous devez d'abord rejoindre la France insoumise.",
            )
