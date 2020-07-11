import numpy

from pathlib import Path
from miping.models.profile import Profile
from miping.models.profileCollection import ProfileCollection
from miping.training.dataPreparation import DataPreparation
from miping.interfaces.helper import Helper
from miping.interfaces.liwc import LiwcAPI


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
            print("Country: " + str(country))

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

                # IBM says they need at least 600 words
                # for analysis, only then we are adding to collection
                if wordCount >= 600:

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
            print(
                "Loading for country: " +
                country
            )
            helper = Helper()

            # initialize progress bar
            numProfiles = len(profileCol.profileList)
            helper.printProgressBar(
                0,
                numProfiles,
                prefix='Progress:',
                suffix='Complete',
                length=50
            )

            # iterate over all profiles, call api
            # and enrich profiles with result
            for num, profile in enumerate(profileCol.profileList):
                profile, errorEncounterd = self.ibm.get_profile(
                    text=profile.text,
                    fillProfile=profile,
                    language=profile.language,
                )
                if errorEncounterd is False:
                    # add profile to collection
                    returnProfileCol.add_profile(profile)

                # Update Progress Bar
                helper.printProgressBar(
                    num + 1,
                    numProfiles,
                    prefix='Progress:',
                    suffix='Complete',
                    length=50
                )

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

    def do_liwc(
        self,
        profileCol,
        country,
        liwcPath,
        fileName,
        readFiles=False,
        writeFiles=False,
        skipInputWait=False
    ):
        """
        TODO do_liwc

        will enrich given profileCol with read LIWC files
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        returnProfileCol = ProfileCollection()

        if readFiles is True:
            print("\nReading files for previous liwc exports")
            print(
                "Loading for country: " +
                country
            )

            # path for saved profiles
            file_directory_string = (
                'data/06' +
                country +
                'liwc_profiles.csv'
            )
            file_path = Path(file_directory_string)

            returnProfileCol.read_profile_list_file(
                full_path=file_path
            )

            print("Files successfully loaded")
        else:
            # path where LIWC results where saved
            file_directory_string = (
                liwcPath +
                country +
                fileName
            )
            file_path = Path(file_directory_string)

            print(
                "\nBegin LIWC loading. This is a manual task. " +
                "Please ensure that LIWC results exist in " +
                "the following location: " +
                str(file_directory_string)
            )
            filesReady = True
            if skipInputWait is False:
                # waiting for any user input
                # so user can create LIWC output files
                val = input("Please confirm with enter when files are ready: ")
                if len(val) > 0:
                    # user provided some input other than enter
                    filesReady = False
                    print("Skipping process")

            if filesReady is True:
                # import liwc results and add to profiles
                liwc = LiwcAPI()
                returnProfileCol = liwc.import_liwc_result(
                    fullPath=file_path,
                    profileCol=profileCol
                )

            # only write file if specified
            if writeFiles is True:
                # path for saving profileCollection
                file_directory_string = (
                    'data/06' +
                    country +
                    'liwc_profiles.csv'
                )
                file_path = Path(file_directory_string)

                returnProfileCol.write_profile_list_file(
                    full_path=file_path
                )
            print("End LIWC loading.")

        return returnProfileCol

    def print_statistics(
        self,
        globalProfileCollection,
    ):
        """
        TODO docstring print_statistics
        """

        print("\nData Preparation Statistics")
        for idx, country in enumerate(globalProfileCollection):
            print("Statistics for: " + str(country))

            locProfileList = globalProfileCollection[country].profileList

            # number of users
            numUsers = len(locProfileList)
            print("Number of users: " + str(numUsers))

            # number of words per user
            print("Number of words")
            numWords = [
                float(getattr(profile, 'numberWords'))
                for profile in locProfileList
            ]
            self.print_min_max_mean_std(numWords)
            # number of tweets
            print("Number of tweets")
            numTweets = [
                float(getattr(profile, 'numberTweets'))
                for profile in locProfileList
            ]
            self.print_min_max_mean_std(numTweets)

            # ibm big 5 data
            locAttrList = [
                'big5_openness',
                'big5_conscientiousness',
                'big5_extraversion',
                'big5_agreeableness',
                'big5_neuroticism'
            ]

            for attr in locAttrList:
                print(attr)
                seq = []
                for profile in locProfileList:
                    value = getattr(profile, attr)
                    if value == '':
                        # append nothing if no value given
                        continue
                    seq.append(float(value))
                self.print_min_max_mean_std(seq)

            # duplicate check (there should be no more than 250 tweets)
            print("User with more than 250 tweets (check for duplicates)")
            for profile in locProfileList:
                if int(getattr(profile, 'numberTweets')) > 250:
                    print(profile)
                    print(profile.userID)
            print(
                "END users with more than 250 tweets " +
                "(if no users shown it's fine)"
            )

        print("Finished\n")
        return

    def print_min_max_mean_std(
        self,
        printList,
    ):
        """
        TODO docstring
        """
        if len(printList) > 0:
            print("MIN: " + str(min(printList)))
            print("MAX: " + str(max(printList)))
            print("Mean: " + str(numpy.mean(printList)))
            print("Standard Deviation" + str(numpy.std(printList)))
        else:
            print('No value in list')

        return
