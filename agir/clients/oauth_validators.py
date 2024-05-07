import oauthlib.common
from oauth2_provider.oauth2_validators import OAuth2Validator

from agir.groups.models import Membership


class CustomOAuth2Validator(OAuth2Validator):
    def get_additional_claims(self, request: oauthlib.common.Request):
        active_memberships = Membership.objects.filter(
            person=request.user.person,
            supportgroup__published=True,
        )


y
