from .modelBase import ModelBase
from sklearn.gaussian_process import GaussianProcessRegressor as skGPR


class GaussianProcessRegressor(ModelBase):
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
            gridSearch = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'n_restarts_optimizer': [0, 2, 10],
                'random_state': [0]
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='GaussianProcessRegressor',
            model=skGPR(),
            gridSearchParams=gridSearch
        )

        return
