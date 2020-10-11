class Helper:
    """
    Helper class for central reused functions
    """

    def __init__(
        self,
    ):
        pass

    def printProgressBar(
        self,
        iteration,
        total,
        prefix='',
        suffix='',
        decimals=1,
        length=100,
        fill='█',
        printEnd="\r"
    ):
        """
        Print progress bar to terminal, e.g. in a loop.

        Parameters
        ----------
        iteration : integer, default=None, required
            current iteration (Int).
        total : integer, default=None, required
            total iterations (Int).
        prefix : string, default=None
            prefix string (Str).
        suffix : string, default=None
            suffix string (Str).
        decimals : integer, default=None
            positive number of decimals in percent complete (Int).
        length : integer, default=None
            character length of bar (Int).
        fill : string, default=None
            bar fill character (Str).
        printEnd : string, default=None
            end character (e.g. "\r", "\r\n") (Str).
        """
        percent = (
            ("{0:." + str(decimals) + "f}").format(
                100 * (iteration / float(total))
            )
        )
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(
            '\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd
        )
        # Print New Line on Complete
        if iteration == total:
            print()

        return
