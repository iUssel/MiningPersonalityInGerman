from sklearn import linear_model


class BayesianRidge:
    """
    TODO docstring Class BayesianRidge
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        TODO init func Class BayesianRidge
        gridSearchParams: dict
        """

        if gridSearchParams is not None:
            self.gridSearchParams = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'n_iterint': [100, 300, 500],
            }

            self.gridSearchParams = defaultParams

        self.name = 'BayesianRidge'

        return

    def getModel(
        self,
    ):
        """
        TODO func getModel
        returns default model
        this will be modified during gridsearch
        """

        model = linear_model.BayesianRidge()

        return model
