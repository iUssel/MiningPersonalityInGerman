from pathlib import Path
from miping.models.profile import Profile
from miping.models.profileCollection import ProfileCollection
from miping.training.dataPreparation import DataPreparation


class PreparationProcess:
    """
    TODO docstring Class PreparationProcess
    """

    def __init__(
        self,
        config,
        ibm=None,
    ):
        """
        TODO init func Class PreparationProcess
        """
        # save config
        self.config = config

        # save ibm object
        self.ibm = ibm

        return

    def do_condense_tweets(
        self,
        verifiedTweetCol,
        verifiedUsers,
        language,
        country,
        readFiles=False,
        writeFiles=False,
    ):
        """
        TODO do_condense_tweets

        returns profile Collection with user texts and ids
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        dataPre = DataPreparation(
        )

        returnProfileCol = ProfileCollection()

        if readFiles is True:
            print("\nReading files for condense tweets")
            print(
                "Loading for country: " +
                country
            )

            # path for saved profiles
            file_directory_string = (
                'data/04condensed' +
                country +
                'profiles.csv'
            )
            file_path = Path(file_directory_string)

            returnProfileCol.read_profile_list_file(
                full_path=file_path
            )

            print("Files successfully loaded")
        else:
            print("\nBegin condensing tweets")

            # iterate over all users to condense their tweets
            # and create a profile to add to profileCollection
            for user in verifiedUsers.userList:
                userID = user.id_str
                # get all saved tweets for this user
                userTweetCol = verifiedTweetCol.get_tweets_of_userid(
                    userID=userID
                )
                # save number of tweets in list
                tweetCount = len(userTweetCol.tweetList)
                # combine all tweets into one string
                textString = userTweetCol.combine_tweet_text()
                # call data cleansing for combined string
                textString = dataPre.clean_text(
                    textString=textString
                )

                # count words (based on any whitespace)
                wordCount = len(textString.split())

                singleProfile = Profile(
                    userID=userID,
                    text=textString,
                    numberWords=wordCount,
                    numberTweets=tweetCount,
                    language=language
                )

                # add profile to collection
                returnProfileCol.add_profile(singleProfile)

            # only write file if specified
            if writeFiles is True:
                # path for saving profileCollection
                file_directory_string = (
                    'data/04condensed' +
                    country +
                    'profiles.csv'
                )
                file_path = Path(file_directory_string)

                returnProfileCol.write_profile_list_file(
                    full_path=file_path
                )
            print("End condensing tweets")

        return returnProfileCol

    def do_get_ibm_profiles(
        self,
        profileCol,
        country,
        readFiles=False,
        writeFiles=False,
    ):
        """
        TODO do_get_ibm_profiles

        calls ibm api for profiles
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        returnProfileCol = ProfileCollection()

        if readFiles is True:
            print("\nReading files for get ibm profiles")
            print(
                "Loading for country: " +
                country
            )

            # path for saved profiles
            file_directory_string = (
                'data/05' +
                country +
                'ibm_profiles.csv'
            )
            file_path = Path(file_directory_string)

            returnProfileCol.read_profile_list_file(
                full_path=file_path
            )

            print("Files successfully loaded")
        else:
            print("\nBegin getting IBM profiles")

            # iterate over all profiles, call api
            # and enrich profiles with result
            for profile in profileCol.profileList:
                profile = self.ibm.get_profile(
                    text=profile.text,
                    fillProfile=profile,
                    language=profile.language,
                )

                # add profile to collection
                returnProfileCol.add_profile(profile)

            # only write file if specified
            if writeFiles is True:
                # path for saving profileCollection
                file_directory_string = (
                    'data/05' +
                    country +
                    'ibm_profiles.csv'
                )
                file_path = Path(file_directory_string)

                returnProfileCol.write_profile_list_file(
                    full_path=file_path
                )
            print("End getting IBM profiles")

        return returnProfileCol
