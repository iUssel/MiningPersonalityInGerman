import yaml
import os
from dotenv import load_dotenv


class ConfigLoader:
    """
    TODO docstring
    """

    config = None

    def __init__(
        self,
        configPath="",
        environmentVars="",
    ):
        """
        TODO init function of ConfigLoader Class
        """

        # .env variables are loaded from file
        load_dotenv()

        if configPath != "":
            self.config = self._funcReadConfig(configPath)
        else:
            raise _InputError(
                "No configPath given. " +
                "You need to pass the full path to config.yml."
            )

        self.environmentVars = self._funcReadEnvironmentVars()

    def _funcReadConfig(
        self,
        path,
    ):
        """
        TODO doc stringt funcReadConfig
        """

        with open(path, "r") as ymlfile:
            config = yaml.safe_load(ymlfile)

        return config

    def _funcReadEnvironmentVars(
        self,
    ):
        """
        TODO func Read Environment Vars
        """

        # retrieve API keys and other secrets from environment variables
        # initialize dict
        apiKeys = {
            'twitter': {},
            'ibm': {}
        }

        apiKeys['twitter']['ConsumerKey'] = (
            os.environ.get("twitter_consumer_key")
        )
        if apiKeys['twitter']['ConsumerKey'] is None:
            raise _InputError(
                "No Twitter consumer key in environment variables. " +
                "See README file."
            )

        apiKeys['twitter']['ConsumerSecrect'] = (
            os.environ.get("twitter_consumer_secret")
        )
        if apiKeys['twitter']['ConsumerSecrect'] is None:
            raise _InputError(
                "No Twitter consumer secret in environment variables. " +
                "See README file."
            )

        apiKeys['twitter']['AccessToken'] = (
            os.environ.get("twitter_access_token")
        )
        if apiKeys['twitter']['AccessToken'] is None:
            raise _InputError(
                "No Twitter access token in environment variables. " +
                "See README file."
            )

        apiKeys['twitter']['AccessTokenSecret'] = (
            os.environ.get("twitter_access_token_secret")
        )
        if apiKeys['twitter']['AccessTokenSecret'] is None:
            raise _InputError(
                "No Twitter access token secret in environment variables. " +
                "See README file."
            )

        return apiKeys


class _InputError(Exception):
    """Internal exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
