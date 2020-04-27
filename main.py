import os
import helper
import miping

from pathlib import Path


def funcMain():
    """TODO Doc string
    """

    # get configuration
    globalConfig, apiKeys = funcInitialize()

    # sample
    print(globalConfig["initial_settings"]["model"])
    print(apiKeys['twitter']['ConsumerKey'])

    twitter = miping.interfaces.TwitterAPI()

def funcInitialize():
    """
    TODO Doc String funcInitialize
    """
    # load configuration
    configPath = Path(os.path.dirname(os.path.abspath(__file__)))
    configFullPath = configPath / "config.yml"
    configHelper = helper.ConfigLoader(configFullPath)
    config = configHelper.config

    # retrieve API keys and other secrets from environment variables
    apiKeys = configHelper.environmentVars

    return config, apiKeys


if __name__ == "__main__":
    funcMain()
