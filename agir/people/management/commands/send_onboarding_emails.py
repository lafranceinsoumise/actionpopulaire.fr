from agir.lib.commands import BaseCommand
from agir.people.actions.subscription import schedule_onboarding_emails


class Command(BaseCommand):
    language = "en"
    help = "Send onboarding emails to new members"
    dry_run = False
    silent = False

    def print_result(self, result):
        if not result:
            self.log(f"✖  Aucun email n'a été envoyé.")

        for type, emails in result.items():
            self.info(f"Type d'inscription : {type}")

            for email, count in emails.items():
                message = (
                    f"{email} ⟶ {count} e-mail{'s' if count != 1 else ''} scheduled"
                )
                if count > 0:
                    self.success(message)
                else:
                    self.error(message)

    def handle(self, **options):
        self.log(f"\n✉ Sending onboarding emails...\n\n")
        result = schedule_onboarding_emails(dry_run=self.dry_run)
        self.print_result(result)
