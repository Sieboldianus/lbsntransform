"""
Tests for command line interface (CLI).
"""
import unittest

from lbsntransform.tools.helper_functions import HelperFunctions as HF  # type: ignore


class TestExtractors(unittest.TestCase):
    """Test various string operations from HelperFunctions"""

    def test_mentions(self):
        """
        Is the user mentioned extracted from the string?
        """
        test_body = "/u/Exz3ssion, vielen Dank f\u00fcr deinen Beitrag. "
        # test Reddit-style @-mentions
        expected_user = "Exz3ssion"
        result = HF.extract_user_mentions(test_body)
        assert expected_user in result
        # test Twitter-style @-mentions
        test_body = "@Exz3ssion, vielen Dank f\u00fcr deinen Beitrag."
        result = HF.extract_atmentions_from_string(test_body)
        assert expected_user in result
        # test Reddit user with a Minus sign
        test_body = (
            "/u/goto-reddit was genau ist eigentlich dein Problem? /u/goto_reddit"
        )
        result = HF.extract_user_mentions(test_body)
        expected_user = ["goto-reddit", "goto_reddit"]
        for user in expected_user:
            assert user in result

    def test_hashtags(self):
        """
        Are all of the hastags extracted from the string?
        """
        test_body = "#germany🇩🇪 #life #green #1234"
        result = HF.extract_hashtags_from_string(test_body)
        expected_tags = {"germany", "life", "green", "1234"}

        unittest.TestCase.assertSetEqual(self, result, expected_tags)


if __name__ == "__main__":
    unittest.main()
