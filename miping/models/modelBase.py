import onnxmltools
from skl2onnx.common.data_types import FloatTensorType
from joblib import dump, load


class ModelBase:
    """
    TODO docstring Class ModelBase
    """

    @staticmethod
    def importModelPickle(
        path
    ):
        """
        TODO doc importModelPickle
        be aware of security issues
        """
        print("Do not import pickle models from unknown sources!")
        # import model from pickle file
        print(
            "Importing pickle from path " +
            str(path)
        )
        answer = input("Confirm action by typing yes: ")
        if answer == "yes":
            model = load(path)
            return model
        else:
            print("Import aborted by user")
            return

    def __init__(
        self,
        labelName="",
        modelName="",
        model=None,
        params=None,
        scores=None,
        gridSearchParams=None,
    ):
        """
        TODO init func Class ModelBase
        """
        # save all variables in class instance
        self.labelName = labelName
        self.modelName = modelName
        self.model = model
        self.params = params
        self.scores = scores
        self.gridSearchParams = gridSearchParams

        return

    def __str__(self):
        return (self.modelName + " for " + self.labelName)

    def getModel(
        self,
    ):
        """
        TODO func getModel
        returns saved model
        """

        return self.model

    def exportModelPickle(
        self,
        path,
    ):
        """
        TODO exportModelPickle func
        """
        print(
            "Exporting pickle of " +
            str(self.__str__()) +
            " to path " +
            str(path)
        )
        dump(self, path)

        return

    def exportModelONNX(
        self,
        path,
        numDim,
        inputName,
    ):
        """
        TODO doc exportModelONNX
        numDim e.g. 93
        inputName e.g. liwc_input
        """
        print(
            "Exporting ONNX of " +
            str(self.__str__()) +
            " to path " +
            str(path)
        )

        # The following line means for example we have a 93-Dimensional
        # float feature vector (-> the LIWC values)
        # and its name is "liwc_input" in ONNX.
        # depends on input variables
        initial_type = [(inputName, FloatTensorType([None, numDim]))]

        # Convert model to ONNX format
        onnx_model = onnxmltools.convert_sklearn(
            model=self.model,
            initial_types=initial_type
        )

        # export model to file
        onnxmltools.utils.save_model(onnx_model, path)

        return onnx_model
