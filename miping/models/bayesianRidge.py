from .modelBase import ModelBase
from sklearn import linear_model


class BayesianRidge(ModelBase):
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
            gridSearch = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'n_iterint': [100, 300, 500],
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='BayesianRidge',
            model=linear_model.BayesianRidge(),
            gridSearchParams=gridSearch
        )

        return
