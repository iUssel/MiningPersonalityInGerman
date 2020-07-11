from sklearn.gaussian_process import GaussianProcessRegressor as skGPR


class GaussianProcessRegressor:
    """
    TODO docstring Class GaussianProcessRegressor
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        TODO init func Class GaussianProcessRegressor
        gridSearchParams: dict
        """

        if gridSearchParams is not None:
            self.gridSearchParams = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'n_restarts_optimizer': [0, 2, 10],
                'random_state': [0]
            }

            self.gridSearchParams = defaultParams

        self.name = 'GaussianProcessRegressor'

        return

    def getModel(
        self,
    ):
        """
        TODO func getModel
        returns default model
        this will be modified during gridsearch
        """

        model = skGPR()

        return model
