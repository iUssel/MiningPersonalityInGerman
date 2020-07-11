from sklearn.svm import SVR


class SupportVectorMachine:
    """
    TODO docstring Class SupportVectorMachine
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        TODO init func Class SupportVectorMachine
        gridSearchParams: dict
        """

        if gridSearchParams is not None:
            self.gridSearchParams = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'kernel': ['rbf', 'sigmoid', 'linear'],
                'C': [0.001, 0.01, 0.1, 1, 10, 100],
                'epsilon': [0.001, 0.01, 0.1, 1, 10],
                'max_iter': [100],
            }

            self.gridSearchParams = defaultParams

        self.name = 'SupportVectorMachine'

        return

    def getModel(
        self,
    ):
        """
        TODO func getModel
        returns default model
        this will be modified during gridsearch
        """

        model = SVR()

        return model
