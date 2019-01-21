from unittest import TestCase
from ..display import str_summary


class DisplayStrSummaryTestCase(TestCase):
    def test_text_longer_than_limit(self):
        s1 = "bonjour je suis une phrase qui va se racourcir."
        s2 = "bonjour je suis une ..."
        self.assertEqual(str_summary(s1, length_max=20), s2)
        self.assertEqual(str_summary(s1, length_max=25), s2)

    def test_text_shorter_than_limit(self):
        s1 = "bonjour je suis une phrase qui va rester tel qu'elle."
        self.assertEqual(str_summary(s1, length_max=len(s1)), s1)

    def test_text_with_last_word_too_long(self):
        s1 = "Une phrase avec un_vraiement_tres_long_dernier_mots le reste peu avoir des espace"
        s2 = "Une phrase avec un_vraiem..."
        self.assertEqual(str_summary(s1, length_max=30, last_word_limit=5), s2)
