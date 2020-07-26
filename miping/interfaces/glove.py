import sqlite3
import pandas
from os import path
from sqlite3 import Error


class GloVe:
    """
    TODO docstring Class GloVe
    """

    def __init__(
        self,
        filePath,
        dataBaseMode=True,
    ):
        """
        TODO init func Class GloVe
        dataBaseMode uses SQLite database instead of direct file
        direct file uses more memory but is independent of external database
        """
        # save in instance
        self.dataBaseMode = dataBaseMode

        if path.exists(filePath) is False:
            # file does not exist
            eString = "Did not find GloVe file passed in GloVe class"
            raise Exception(eString)

        if dataBaseMode is True:
            print("Using GloVe database")
            self.connection = self._create_connection(
                db_file=filePath
            )
        else:
            print("Using GloVe file")
            # load pre trained GloVe word embedding
            glove_df = self.loadGloVeFile(
                glovePath=filePath
            )

            self.glove_df = glove_df

        return

    def getGloVeByWordList(
        self,
        wordList
    ):
        """
        TODO getGloVeByWordList doc
        :param conn: the Connection object
        :param wordList:
        :return:
        """

        if self.dataBaseMode is True:
            # since sqlite is limited in its query length
            # 999 chunks
            apiChunks = 999
            chunks = [
                wordList[
                    x:x+apiChunks
                ] for x in range(0, len(wordList), apiChunks)
            ]
            chunkCollectionDF = pandas.DataFrame()
            # for each 999er chunk, we will perform an SQL request
            for chunkList in chunks:
                # compose sql with length of chunk of word list
                # so that question marks ? can be added
                sql = "SELECT * FROM glove WHERE words IN ({seq})".format(
                        seq=','.join(['?']*len(chunkList))
                    )
                # query database and get data frame with unique values
                unique_glove_df = pandas.read_sql_query(
                    con=self.connection,
                    sql=sql,
                    params=chunkList,
                    index_col='words'
                )
                # add to data frame
                chunkCollectionDF = chunkCollectionDF.append(unique_glove_df)
            # make returned rows unique
            # due to chunks some duplicates are possible
            completeUniqueDF = chunkCollectionDF.drop_duplicates()
            # since returned values are unique we have to get the intersection
            # including duplicates now
            glove_val_df = (
                completeUniqueDF.loc[
                    completeUniqueDF.index.intersection(wordList)
                ]
            )
        else:
            # get values from loaded glove
            glove_val_df = (
                self.glove_df.loc[self.glove_df.index.intersection(wordList)]
            )

        return glove_val_df

    def get_index_list(
        self,
    ):
        """
        TODO get_index_list
        """

        # depending on data if data base mode or not
        if self.dataBaseMode is True:
            # get index as list from data base
            sql = "SELECT words FROM glove;"
            dataFrame = pandas.read_sql_query(
                con=self.connection,
                sql=sql,
                index_col='words'
            )
            # convert to list
            index_list = list(dataFrame.index)
        else:
            # get index from fully loaded glove
            index_list = list(self.glove_df.index)

        return index_list

    def _create_connection(
        self,
        db_file
    ):
        """ TODO create a database connection to the SQLite database
            specified by db_file
            :param db_file: database file
            :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            return conn
        except Error as e:
            print(e)

        return conn

    def loadGloVeFile(
        self,
        glovePath
    ):
        """
        TODO func loadGloVe
        """

        print("\nLoading GloVe")

        # file exists, so we load it
        glove_df = pandas.read_csv(
            filepath_or_buffer=glovePath,
            sep=" ",
            header=None,
            encoding='utf_8',
        )
        # set words as index
        glove_df.set_index(0, inplace=True)
        glove_df.rename_axis("words", axis="index", inplace=True)

        print(
            "GloVe loaded with " +
            str(len(glove_df)) +
            " as count of words."
        )

        return glove_df
