import numpy

from pathlib import Path
from miping.models.profile import Profile
from miping.models.profileCollection import ProfileCollection
from miping.training.dataPreparation import DataPreparation
from miping.interfaces.helper import Helper
from miping.interfaces.liwc import LiwcAPI
from miping.models import TweetCollection


class PreparationProcess:
    """
    Wrapper class for data preparation process (2nd step).
    Contains all functions needed for preparation. Calls mostly miping
    module functions and allows imports and exports of data via csv.
    """

    def __init__(
        self,
        config,
        ibm=None,
        twitter=None,
    ):
        """
        Init function to save configuration and API objects.

        Parameters
        ----------
        config : dict, default=None, required
            Configuration object as returned from ConfigLoader class.
        ibm : miping.interfaces.IbmAPI, default=None
            Initialized IbmAPI object, ready for calls.
        twitter : miping.interfaces.TwitterAPI, default=None
            Initialized TwitterAPI object, ready for calls.
        """
        # save config
        self.config = config

        # save ibm object
        self.ibm = ibm

        # save twitter api object
        self.twitter = twitter

        return

    def hydrate_users(
        self,
        country,
    ):
        """
        Fetch and return user profiles and tweet list for user ID list
        in CSV file.

        Twitter allows only to pass tweet and user IDs, when publicly sharing
        scraped data. This function allows to import a CSV file containing
        only user IDs and automatically fetching related user objects and
        for each user up to the latest 250 tweets. Private users are skipped.
        The CSV file path is hard coded.
        Expected CSV path: 'data/04' + country + 'UserIDs.csv'

        Parameters
        ----------
        country : string, default=None, required
            The country parameter is used to differentiate between CSV files.
            The country name is automatically added to the file name. It
            should match a country given in the global config.

        Returns
        -------
        tweetCol : miping.models.TweetCollection
            Data model type in miping module. Contains the retrieved tweets
            for all given users.
        usersCol : miping.models.UserCollection
            Data model type in miping module. Contains user objects as
            returned by Twitter API.
        """
        # load user ids from file
        # path for saved profiles
        file_directory_string = (
            'data/04' +
            country +
            'UserIDs.csv'
        )
        file_path = Path(file_directory_string)

        # read in user ids
        profileCol = ProfileCollection()
        profileCol.read_profile_list_file(
            full_path=file_path,
            idsonly=True
        )

        # extract userIDs as list
        idList = [obj.userID for obj in profileCol.profileList]
        # create user object
        usersCol = self.twitter.getUsersByList(idList)

        # create tweet collection for return
        tweetCol = TweetCollection(
            additionalAttributes=self.config["twitter"]["add_attributes"]
        )
        for user in usersCol.userList:
            # get tweets for given user
            singleTweetCol = self.twitter.funcGetTweetListByUser(
                    userID=user.id_str,
                    limit=250,
            )
            # add to total collection
            tweetCol.add_tweet_collection(singleTweetCol)

        print("Hydration finished")

        return tweetCol, usersCol

    def do_condense_tweets(
        self,
        verifiedTweetCol,
        verifiedUsers,
        language,
        country,
        readFiles=False,
        writeFiles=False,
        hydrateUsers=False,
    ):
        """
        Actual data preparation for each user. Combining tweets to string.

        This function allows to import and export results via CSV. When
        importing the actual program code is skipped.
        Expected CSV path: 'data/04condensed' + country + 'profiles.csv'.
        It is possible to start this process with just a list of
        user ids, then hydrate_users() has to be called first.
        For each user in the list all tweets are combined into a single
        string. Then the cleaning function is called to remove
        unwanted characters. Only if the resulting string has 600 or
        more space separated tokens, a Profile object is created for that
        user.

        Parameters
        ----------
        verifiedTweetCol : miping.models.TweetCollection, default=None, req
            Previously collected tweets as tweet collection. Contains all
            tweets that should be condensed and combined with the
            user objects.
        verifiedUsers : miping.models.UserCollection, default=None, req
            Previously collected users as user collection. These will be
            combined with the tweet collection.
        language : string, default=None, required
            Language (two letter ISO code) for given contry
            (as specified in config).
        country : string, default=None, required
            Country name of where the passed users are collected from
            (as specified in config)
        readFiles : boolean, default=False
            If True, CSV files will be read instead of following program
            logic.
        writeFiles : boolean, default=False
            Can only be True, if readFiles is False. If True, will export
            results to CSV files. Allows to read files in the next program
            run.
        hydrateUsers : boolean, default=False
            Only True, if readFiles is False. Will call hydrate_users() and
            and take its results as input for condensing. In this case
            verifiedTweetCol and verifiedUsers can be passed as empty
            objects.

        Returns
        -------
        returnProfileCol : miping.models.ProfileCollection
            Profile collection containing all profiles created.
            Profiles include tweets and users.
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

            if hydrateUsers is True:
                print("Hydrating user ids from file")
                verifiedTweetCol, verifiedUsers = self.hydrate_users(
                    country=country
                )

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
        Query IBM API for given ProfileCollection for personality scores.

        Allows imports and exports of results via CSV. Expected path is
        'data/05' + country + 'ibm_profiles.csv'. For each profile
        in given profile collection, IBM API is called and the existing
        profile enriched by IBM personality information. Result
        is returned as enriched profile collection. If errors occur for
        a user (e.g. too few words), this user will be excluded.
        A progress bar is shown during this process. Note that IBM
        does not support all languages.

        Parameters
        ----------
        profileCol : miping.models.ProfileCollection, default=None, required
            Profile collection that should be enriched.
        country : string, default=None, required
            Country name of where the passed users are collected from
            (as specified in config)
        readFiles : boolean, default=False
            If True, CSV files will be read instead of following program
            logic.
        writeFiles : boolean, default=False
            Can only be True, if readFiles is False. If True, will export
            results to CSV files. Allows to read files in the next program
            run.

        Returns
        -------
        returnProfileCol : ProfileCollection
            New IBM enriched ProfileCollection based on the input collection.
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
        Return enriched profiles with LIWC data from separate file.

        Allows imports and exports of results via CSV. Expected path is
        'data/06' + country + 'liwc_profiles.csv'.
        The input profile collection contains tweet and user data and
        should be enriched with LIWC data. Since LIWC is a standalone
        program it cannot be integrated into the Python program.
        The user is asked to manually prepare the previously exported
        profile collection with LIWC and then export the LIWC results.
        These results are saved in CSV format in liwcPath and fileName.
        From there they are imported via LIWC API and enrich the existing
        profiles.

        Parameters
        ----------
        profileCol : ProfileCollection, default=None, required
            Input profile collection which should be enriched with LIWC data.
        country : string, default=None, required
            Country name of where the passed users are collected from
            (as specified in config)
        liwcPath : string, default=None, required
            Relative path of where the LIWC export is saved.
        fileName : string, default=None, required
            File name for LIWC export.
        readFiles : boolean, default=False
            If True, CSV files will be read instead of following program
            logic.
        writeFiles : boolean, default=False
            Can only be True, if readFiles is False. If True, will export
            results to CSV files. Allows to read files in the next program
            run.
        skipInputWait : boolean, default=False
            If False, the user needs to manually confirm by pressing enter
            that the LIWC export is ready for import. If True, this
            confirmation step is skipped and the program assumes the
            file already exists.

        Returns
        -------
        returnProfileCol : ProfileCollection
            New LIWC enriched ProfileCollection based on the input collection.
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
        Print descriptive statistics for given profile collections.

        The given dictionary contains one profile collection for
        each country. Information will be printed about the number
        of users, number of words, number of tweets, and the Big
        Five personality scores.
        In the end and additional check is carried out to see if any
        user has more than 250 tweets in the collection. Since we
        selected only 250 tweets for each user, more tweets would
        indicate that we accidentally selected this user twice.

        Parameters
        ----------
        globalProfileCollection : dict, default=None, required
            Dictionary containing profile collections for each country.
            For each collection the descriptive statistics are printed.
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
                    if value == '' or value is None:
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
        percentile=False
    ):
        """
        Print min, max, mean, std, and 25th and 75th percentile for values.

        Parameters
        ----------
        printList : list, default=None, required
            List containing numeric values for which descriptive statistics
            should be calculated and printed.
        percentile : boolean, default=False
            If True, additionally 25th and 75th percentile are printed.
        """
        if len(printList) > 0:
            print("MIN: " + str(min(printList)))
            if percentile is True:
                print("25th percentile: ", numpy.percentile(printList, 25))
                print("75th percentile: ", numpy.percentile(printList, 75))
            print("MAX: " + str(max(printList)))
            print("Mean: " + str(numpy.mean(printList)))
            print("Standard Deviation: " + str(numpy.std(printList)))
        else:
            print('No value in list')

        return
