import csv
from .profile import Profile


class ProfileCollection:
    """
    TODO docstring Class ProfileCollection
    """

    def __init__(
        self,
    ):
        """
        TODO init func Class ProfileCollection
        """
        # initialize empty list to collect profiles
        self.profileList = []

        return

    def add_profile(
        self,
        profileObj: Profile,
    ):
        """
        TODO add_profile
        """

        self.profileList.append(profileObj)

        return

    def write_profile_list_file(
        self,
        full_path='profilelist.csv',
    ):
        """
        TODO docstring
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

                writer.writerow(basicList)

        return

    def read_profile_list_file(
        self,
        full_path='profilelist.csv',
    ):
        """
        TODO docstring read_profile_list_file
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

                # we will read all attributes column by column
                # via the profiles attribute list
                for num, attr in enumerate(Profile.attributeNameList):
                    # 0 based index
                    # read column as attribute
                    setattr(profileInst, attr, row[num])

                # add profile to collection
                self.add_profile(profileInst)

        return
