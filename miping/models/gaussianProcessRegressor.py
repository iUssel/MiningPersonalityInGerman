from .modelBase import ModelBase
from sklearn.gaussian_process import GaussianProcessRegressor as skGPR
# from sklearn.gaussian_process.kernels import RBF
from sklearn.gaussian_process.kernels import ConstantKernel
from sklearn.gaussian_process.kernels import Matern, WhiteKernel


class GaussianProcessRegressor(ModelBase):
    """
    GaussianProcessRegressor Subclass of ModelBase
    """

    def __init__(
        self,
        gridSearchParams=None,
    ):
        """
        Init function calling super constructor and setting the model.
        Setting the kernel.

        Parameters
        ----------
        gridSearchParams : dict, default=None
            Dictionary containing all parameters that should be
            considered during grid search.
        """
        # standard kernel
        # kernel = 1.0 * RBF(1.0)

        # custom kernel
        kernel = ConstantKernel() + Matern() + WhiteKernel()

        if gridSearchParams is not None:
            gridSearch = gridSearchParams
        else:
            # applying default parameters
            defaultParams = {
                'n_restarts_optimizer': [3],
                'random_state': [0]
            }

            gridSearch = defaultParams

        super().__init__(
            modelName='GaussianProcessRegressor',
            model=skGPR(kernel=kernel),
            gridSearchParams=gridSearch
        )

        return
