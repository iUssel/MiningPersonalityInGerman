from .modelBase import ModelBase
from sklearn import linear_model


class RidgeRegression(ModelBase):
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
            gridSearch = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'alpha': [0.1, 1.0, 10.0],
                'random_state': [0]
            }
            gridSearch = defaultParams

        super().__init__(
            modelName='RidgeRegression',
            model=linear_model.Ridge(),
            gridSearchParams=gridSearch
        )

        return
