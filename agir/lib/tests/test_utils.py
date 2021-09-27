from hypothesis import strategies as st, given
from hypothesis.extra.django import TestCase as HypothesisTestCase

from agir.lib.utils import grouper


class GrouperTestCase(HypothesisTestCase):
    @given(st.integers(min_value=1, max_value=1000), st.lists(st.integers()))
    def test_splits_correctly(self, n, l):
        groups = [list(g) for g in grouper(l, n)]

        for g in groups[:-1]:
            self.assertEqual(len(g), n)

        if l:
            self.assertLessEqual(len(groups[-1]), n)

        self.assertEqual([e for g in groups for e in g], l)
