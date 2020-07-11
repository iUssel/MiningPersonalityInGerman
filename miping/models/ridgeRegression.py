from sklearn import linear_model


class RidgeRegression:
    """
    TODO docstring Class RidgeRegression
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        TODO init func Class DecisionTree
        gridSearchParams: dict
        """

        if gridSearchParams is not None:
            self.gridSearchParams = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'alpha': [0.1, 1.0, 10.0],
                'random_state': [0]
            }

            self.gridSearchParams = defaultParams

        self.name = 'RidgeRegression'

        return

    def getModel(
        self,
    ):
        """
        TODO func getModel
        returns default model
        this will be modified during gridsearch
        """

        model = linear_model.Ridge()

        return model
