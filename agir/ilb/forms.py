from agir.donations.base_forms import BaseDonorForm


class PersonalInformationForm(BaseDonorForm):
    show_subscribed = False

    def __init__(self, payments_modes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        del self.fields["declaration"]
        del self.fields["fiscal_resident"]
