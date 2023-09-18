from unittest import TestCase

from hypothesis import strategies as st, given
from hypothesis.extra.django import TestCase as HypothesisTestCase

from agir.lib.utils import grouper, get_youtube_video_id


class GrouperTestCase(HypothesisTestCase):
    @given(st.integers(min_value=1, max_value=1000), st.lists(st.integers()))
    def test_splits_correctly(self, n, l):
        groups = [list(g) for g in grouper(l, n)]

        for g in groups[:-1]:
            self.assertEqual(len(g), n)

        if l:
            self.assertLessEqual(len(groups[-1]), n)

        self.assertEqual([e for g in groups for e in g], l)


class YoutubeVideoIDfromURLTestCase(TestCase):
    expected_id = "ZZ5LpwO-An4"
    valid_urls = [
        "http://youtu.be/ZZ5LpwO-An4",
        "www.youtube.com/watch?v=ZZ5LpwO-An4&feature=feedu",
        "http://www.youtube.com/embed/ZZ5LpwO-An4",
        "http://www.youtube.com/v/ZZ5LpwO-An4?version=3&amp;hl=en_US",
        "https://www.youtube.com/watch?v=ZZ5LpwO-An4&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6",
        "youtube.com/watch?v=ZZ5LpwO-An4",
        "youtu.be/watch?v=ZZ5LpwO-An4",
        "http://www.youtube.com/watch?v=ZZ5LpwO-An4",
        "http://www.youtube.com/v/ZZ5LpwO-An4",
        "http://www.youtube.com/e/ZZ5LpwO-An4",
        "http://www.youtube.com/watch?feature=player_embedded&v=ZZ5LpwO-An4",
        "http://www.youtube.com/?feature=player_embedded&v=ZZ5LpwO-An4",
        "http://www.youtube.com/?v=ZZ5LpwO-An4",
    ]
    invalid_urls = [
        "http://www.youtube.com/user/username#p/u/11/ZZ5LpwO-An4",
        "http://www.youtube.com/sandalsResorts#p/c/54B8C800269D7C1B/0/ZZ5LpwO-An4",
        "https://visio.lafranceinsoumise.fr/ZZ5LpwO-An4",
        "http://not-youtube/watch?v=ZZ5LpwO-An4",
        "https://www.youtube.evil/embed/ZZ5LpwO-An4",
    ]

    def test_should_extract_id_from_valid_urls(self):
        for url in self.valid_urls:
            id = get_youtube_video_id(url)
            self.assertEqual(id, self.expected_id, url)

    def test_should_not_extract_id_from_invalid_urls(self):
        for url in self.invalid_urls:
            with self.assertRaises(ValueError, msg=url):
                get_youtube_video_id(url)


def multipartify(data, parent_key=None, formatter: callable = None) -> dict:
    """
    https://gist.github.com/kazqvaizer/4cebebe5db654a414132809f9f88067b
    :param data: The data dictionary
    :param parent_key: The parent key to use as a suffix
    :param formatter: A formatter function for the value
    :return: A flatten dictionary
    """
    if formatter is None:
        formatter = lambda v: (None, v)  # Multipart representation of value

    if type(data) is not dict:
        return {parent_key: formatter(data)}

    converted = []

    for key, value in data.items():
        current_key = key if parent_key is None else f"{parent_key}.{key}"
        if type(value) is dict:
            converted.extend(multipartify(value, current_key, formatter).items())
        elif type(value) is list:
            for ind, list_value in enumerate(value):
                iter_key = f"{current_key}[{ind}]"
                converted.extend(multipartify(list_value, iter_key, formatter).items())
        else:
            converted.append((current_key, formatter(value)))

    return dict(converted)
