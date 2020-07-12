from .modelBase import ModelBase
from sklearn.svm import SVR


class SupportVectorMachine(ModelBase):
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
            gridSearch = gridSearchParams
        else:
            # TODO applying best default parameters
            defaultParams = {
                'kernel': ['rbf', 'sigmoid', 'linear'],
                'C': [0.001, 0.01, 0.1, 1, 10, 100],
                'epsilon': [0.001, 0.01, 0.1, 1, 10],
                'max_iter': [100],
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='SupportVectorMachine',
            model=SVR(),
            gridSearchParams=gridSearch
        )

        return
