
import onnxruntime as oonxrt
import numpy

from .modelBase import ModelBase


class OnnxModel(ModelBase):
    """
    TODO docstring Class OnnxModel
    just for prediction, no training
    """

    def importModelONNX(
        self,
        path
    ):
        """
        TODO doc importModelONNX

        returns bytes
        """

        # import model from onnx file
        print(
            "Importing ONNX model from path " +
            str(path)
        )
        with open(path, "rb") as in_file:
            # onnx model is needed as bytes
            data = in_file.read()

        self._trainedOnnxModel = data

        return

    def __init__(
        self,
        modelName,
        labelName,
        trainedOnnxModel=None,
    ):
        """
        TODO init func Class DecisionTree
        """

        # onnx model just for internal use
        self._trainedOnnxModel = trainedOnnxModel

        super().__init__(
            modelName=modelName,
            labelName=labelName,
            # passing self, so that when predict function is called on
            # model, this will call the predict function we implemented
            # here
            model=self,
        )

        return

    def predict(
        self,
        X
    ):
        """
        TODO doc predict
        imitates scikits predict function
        X -> features for prediction
        """

        if self._trainedOnnxModel is None:
            raise Exception("Empty ONNX Model")

        # prepare sessions for onnx
        sess = oonxrt.InferenceSession(self._trainedOnnxModel)
        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[0].name
        # perform prediction with onnx model
        pred_onx = sess.run(
            [label_name], {input_name: X.astype(numpy.float32)}
        )[0]

        pred_onx_flat = pred_onx.flatten()

        return pred_onx_flat

    def fit(
        self,
        X,
        y
    ):
        """
        TODO doc fit
        as a measure, to prevent false usage with onnx model
        """
        raise Exception(
            "ONNX models are only for prediction" +
            "Training via fit function not possible."
        )
