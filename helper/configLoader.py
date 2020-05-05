import yaml
import os
from dotenv import load_dotenv


class ConfigLoader:
    """
    TODO docstring
    """

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
            'ibm': {},
            'google': {},
        }

        apiKeys['twitter']['ConsumerKey'] = (
            os.environ.get("twitter_consumer_key")
        )
        if apiKeys['twitter']['ConsumerKey'] is None:
            raise _InputError(
                "No Twitter consumer key in environment variables. " +
                "See README file."
            )

        apiKeys['twitter']['ConsumerSecret'] = (
            os.environ.get("twitter_consumer_secret")
        )
        if apiKeys['twitter']['ConsumerSecret'] is None:
            raise _InputError(
                "No Twitter consumer secret in environment variables. " +
                "See README file."
            )

        apiKeys['twitter']['AccessToken'] = (
            os.environ.get("twitter_access_token")
        )
        if apiKeys['twitter']['AccessToken'] is None:
            print(
                'No Twitter access token supplied. ' +
                'Streaming will be disabled.'
            )

        apiKeys['twitter']['AccessTokenSec'] = (
            os.environ.get("twitter_access_token_sec")
        )
        if apiKeys['twitter']['AccessTokenSec'] is None:
            print(
                'No Twitter access token secret supplied. ' +
                'Streaming will be disabled.'
            )

        apiKeys['google']['maps'] = (
            os.environ.get("google_places_api")
        )
        if apiKeys['google']['maps'] is None:
            print(
                'No Google Places API key supplied. ' +
                'Locations lookup will be disabled. ' +
                'Only necessary if scraping is True.'
            )

        return apiKeys


class _InputError(Exception):
    """Internal exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message