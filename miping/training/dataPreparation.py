import re


class DataPreparation:
    """
    All relevant data preparation steps are combined in this class.
    """

    def __init__(
        self,
    ):
        pass

    def clean_text(
        self,
        textString,
    ):
        """
        Apply data cleansing to given text.

        Turn all to lower case.
        Remove URLs.
        Pad hashtags with space.
        Remove mentions.
        Add spaces around punctuations.
        Remove double spaces in result.

        Parameters
        ----------
        textString : string, default=None, required
            Text that should be cleaned.

        Returns
        -------
        textString : string
            Cleaned text.
        """

        # set to lower case
        textString = textString.lower()

        # remove URLs
        httpPattern = re.compile(
            (
                r'https?:\/\/(www\.)?[-a-zA-Z0–9@:%._\+~#=]' +
                r'{1,256}\.[a-z]{2,6}' +
                r'\b([-a-zA-Z0–9@:%_\+.~#?&//=]*)\S+'
            ),
            re.MULTILINE
        )
        urlPattern = re.compile(
            (
                r'[-a-zA-Z0–9@:%._\+~#=]{1,256}\.[a-z]{2,6}' +
                r'\b([-a-zA-Z0–9@:%_\+.~#?&//=]*)\S+'
            ),
            re.MULTILINE
        )
        # to remove links that start with HTTP/HTTPS in the tweet
        textString = re.sub(httpPattern, '', textString)
        # to remove other url links (like linkshortener URLs)
        textString = re.sub(urlPattern, '', textString)

        # replace # symbol with ' # ' (space hashtag and space)
        # so we can count number of hashtags and have
        # the word used as a hashtag
        textString = textString.replace('#', ' # ')

        # remove mentions
        # starts with whitespace and @
        # then include everything until next whitespace
        textString = re.sub(r'\s@\S+', '', textString)

        # add spaces around punctuations
        # helps when applying word embeddings
        # punctuations excluding @ and #
        textString = re.sub(
            r'([!()-[\]{};:+\'"\,<>./?$%^&*_~])',
            r' \1 ',
            textString
        )
        # remove succeeding spaces, so always only one space
        textString = re.sub(r'\s{2,}', ' ', textString)

        return textString
