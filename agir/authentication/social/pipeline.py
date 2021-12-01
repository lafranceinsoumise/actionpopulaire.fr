from django.contrib import messages
from django.utils.safestring import mark_safe


def add_message(backend, user, details, new_association, *args, **kwargs):
    request = backend.strategy.request
    email = details.get("email")

    if request is not None:
        if user:
            if new_association:
                if not user.person.emails.filter(address=email).exists():
                    message = (
                        f"Votre compte Facebook a bien été relié à votre compte la France insoumise. "
                        f"Vous pourrez désormais l'utiliser pour vous connecter."
                    )
                else:
                    message = f"Votre compte Facebook a bien été relié à votre compte la France insoumise via votre adresse email {email}"
                messages.add_message(
                    request=request,
                    level=messages.SUCCESS,
                    message=message,
                )
        else:
            messages.add_message(
                request=request,
                level=messages.ERROR,
                message=mark_safe(
                    f"Vous n'avez pas de compte sur la France insoumise avec l'adresse email {email}. "
                    "Si vous possédez un compte avec une autre adresse email, vous pouvez vous connecter avec cette adresse, "
                    "puis associer votre compte France insoumise à votre compte Facebook. "
                    'Si vous n\'avez pas de compte, vous devez <a href="https://lafranceinsoumise.fr/">rejoindre'
                    "la France insoumise</a>."
                ),
            )
