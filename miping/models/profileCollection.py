import csv
from .profile import Profile


class ProfileCollection:
    """
    Collection of Profile objects
    """

    def __init__(
        self,
    ):
        """
        Creates empty profileList
        """
        # initialize empty list to collect profiles
        self.profileList = []

        return

    def add_profile(
        self,
        profileObj: Profile,
    ):
        """
        Add Profile to profileList.

        Parameters
        ----------
        profileObj : Profile, default=None, required
            Profile object instance.
        """

        self.profileList.append(profileObj)

        return

    def write_profile_list_file(
        self,
        full_path='profilelist.csv',
    ):
        """
        Export profiles in profile list to one CSV file.

        Parameters
        ----------
        full_path : string, default='profilelist.csv'
            Full path for export file.
        """

        # write output csv file
        with open(full_path, "w", newline='', encoding='utf-8') as outfile:
            # initialize csv writer
            writer = csv.writer(
                outfile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            # write a row for each profile
            for entry in self.profileList:
                basicList = []
                # for each attribute (id, text, traits etc.)
                # append it to the list to write it to file
                for attr in Profile.attributeNameList:
                    basicList.append(getattr(entry, attr))

                # write liwc categories (even if they are empty)
                for attr in Profile.liwc_category_list:
                    basicList.append(getattr(entry, attr))

                writer.writerow(basicList)

        return

    def read_profile_list_file(
        self,
        full_path='profilelist.csv',
        idsonly=False,
    ):
        """
        Import profiles to profile list from one CSV file.

        Parameters
        ----------
        full_path : string, default='profilelist.csv'
            Full path for import file.
        idsonly : boolean, default=False
            Indicates if file contains only user ids.
        """

        # read csv file
        with open(full_path, "r", newline='', encoding='utf-8') as infile:
            # initialize csv reader
            reader = csv.reader(
                infile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            for row in reader:
                # convert to profile object
                profileInst = Profile()

                if idsonly is False:
                    # standard read in
                    # we will read all attributes column by column
                    # via the profiles attribute list
                    counter = 0
                    for num, attr in enumerate(Profile.attributeNameList):
                        # 0 based index
                        # read column as attribute
                        setattr(profileInst, attr, row[num])
                        counter = num

                    # counter indicates the column index already read
                    # we will add 1, since that is the next column we
                    # want to read
                    counter = counter + 1

                    # read liwc categories column by column
                    for num, attr in enumerate(Profile.liwc_category_list):
                        # 0 based index
                        # read column as attribute
                        setattr(profileInst, attr, row[num+counter])
                else:
                    # idsonly is True, so the file contains only userIDs
                    profileInst.userID = row[0]

                # add profile to collection
                self.add_profile(profileInst)

        return

    def get_profile_by_user_id(
        self,
        userID
    ):
        """
        Search and return profile in profile list with given user id.

        Parameters
        ----------
        userID : string, default=None, required
            User id to search for in profileList.

        Returns
        -------
        userProfile : Profile
            Profile with matching user id.
        """

        # filter current profile list to get profile
        # with corresponding userID
        userProfileList = [
            profile for profile in self.profileList if profile.userID == userID
        ]

        # if more than one profile, something went wrong
        if len(userProfileList) > 1:
            raise Exception(
                "Error in ProfileCollection while retrieving user" +
                "profile by userID. More than one profile matched."
            )

        # get first occurence
        userProfile = userProfileList[0]

        return userProfile
