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
        modelConfigPath="",
    ):
        """
        TODO init function of ConfigLoader Class
        """

        # .env variables are loaded from file
        load_dotenv()

        if configPath != "" and modelConfigPath != "":
            self.config = self._funcReadConfig(configPath)

            # load model parameters config
            self.config_models = self._funcReadConfig(modelConfigPath)
        else:
            raise _InputError(
                "No configPath given. " +
                "You need to pass the full path to config.yml and " +
                "config_model_parameters.yml."
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

        apiKeys['ibm']['url'] = (
            os.environ.get("IBM_URL")
        )
        if apiKeys['ibm']['url'] is None:
            print('No IBM URL in .env')
        apiKeys['ibm']['api'] = (
            os.environ.get("IBM_IAM_APIKEY")
        )
        if apiKeys['ibm']['api'] is None:
            print('No IBM API key in .env')

        return apiKeys


class _InputError(Exception):
    """Internal exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
