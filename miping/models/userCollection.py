import csv
from .user import User


class UserCollection:
    """
    TODO docstring Class UserCollection
    """

    def __init__(
        self,
    ):
        """
        TODO init func Class UserCollection
        """
        # initialize empty list to collect tweets
        self.userList = []

    def funcAddUser(
        self,
        userObj: User,
    ):
        """
        TODO funcAddUser
        """

        self.userList.append(userObj)

        return

    def write_user_list_file(
        self,
        full_path='userlist.csv',
        ids_only=False
    ):
        """
        TODO docstring write_user_list_file
        Write all from user list to file

        if ids_only True it will write only one column
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
            # write a row for each user
            for entries in self.userList:
                basicList = []
                basicList.append(entries.id_str)

                # only if bool is true, we write more than ID
                if ids_only is False:
                    basicList.append(entries.screen_name)
                    basicList.append(entries.followers)
                    basicList.append(entries.tweet_count)
                    basicList.append(entries.location)

                writer.writerow(basicList)

        return

    def read_user_list_file(
        self,
        full_path='userlist.csv',
        ids_only=False,
    ):
        """
        TODO docstring read_user_list_file
        Read all tweets from user list file
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
                # convert to custom user object
                userInstance = User()
                userInstance.id_str = row[0]

                # only if False, we read other attributes
                if ids_only is False:
                    userInstance.screen_name = row[1]
                    userInstance.followers = row[2]
                    userInstance.tweet_count = row[3]
                    userInstance.location = row[4]

                # add user to collection
                self.funcAddUser(userInstance)

    def get_id_list(
        self,
    ):
        """
        TODO docstring get_id_list
        Return list with ids of list
        """

        idList = list(user.id_str for user in self.userList)

        return idList
