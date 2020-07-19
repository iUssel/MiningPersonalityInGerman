import miping.models as mipingModels

from pathlib import Path

from miping.training.features import Features
from miping.training.modelTraining import ModelTraining


class TrainingProcess:
    """
    TODO docstring Class trainingProcess
    """

    def __init__(
        self,
        config,
        modelConfig,
    ):
        """
        TODO init func Class trainingProcess
        """

        self.config = config
        self.modelConfig = modelConfig

        return

    def createLIWCModels(
        self,
    ):
        """
        TODO docstring createModels

        returns modelList
        """
        # this will contain all model instances that we want to train
        modelList = []

        # list of models to be created
        # easier to do it dynamically
        loadModels = [
            'BayesianRidge',
            #'DecisionTree',
            #'GaussianProcessRegressor',
            #'RandomForest',
            'RidgeRegression',
            #'SupportVectorMachine'
        ]

        # gridsearch parameters from config
        gridParams = self.modelConfig['liwcModelSelection']

        # create model instances with grid search parameters
        # loaded from config
        for loadModel in loadModels:
            # load config for this model
            params = gridParams[loadModel]
            # get model class
            class_ = getattr(mipingModels, loadModel)
            modelInstance = class_(
                gridSearchParams=params
            )
            # add model to list
            modelList.append(modelInstance)

        return modelList

    def doLIWCModelTraining(
        self,
        profileCol,
        writePickleFiles=False,
        readPickleFiles=False,
        writeONNXModel=False,
        readONNXModel=False,
    ):
        """
        TODO doLIWCModelTraining
        """

        if writePickleFiles is True and readPickleFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        if writeONNXModel is True and readONNXModel is True:
            raise Exception(
                "writeONNXModel and readONNXModel cannot be " +
                "True at the same time."
            )

        if readPickleFiles is True and readONNXModel is True:
            raise Exception(
                "readPickleFiles and readONNXModel cannot be " +
                "True at the same time."
            )

        if readPickleFiles is True:
            print("\nReading files for LIWC model training from pickle")
            # load models in this dict
            globalTrainedModels = {}
            # load models (one for each label (big 5 dimension))
            for label in self.config['labelsGlobalList']:
                # path for saved trained models
                file_directory_string = (
                    'data/trainedModels/'
                )
                # concatenate file path
                file_path = Path(
                    file_directory_string +
                    label +
                    ".pickle"
                )
                # call import function for model
                impModel = mipingModels.ModelBase.importModelPickle(
                    file_path
                )
                globalTrainedModels[label] = impModel

            for key, model in globalTrainedModels.items():
                # print model names to confirm which models are loaded
                print(model.__str__())
            print("Pickle import finished")

        elif readONNXModel is True:
            print("\nReading files for LIWC model training from ONNX")
            # load models in this dict
            globalTrainedModels = {}
            # load models (one for each label (big 5 dimension))
            for label in self.config['labelsGlobalList']:
                # path for saved trained models
                file_directory_string = (
                    'data/trainedModels/'
                )
                # concatenate file path
                file_path = Path(
                    file_directory_string +
                    label +
                    ".ONNX"
                )
                # import onnx model
                onnx = mipingModels.OnnxModel(
                    modelName="ONNX Model",
                    labelName=label,
                )
                onnx.importModelONNX(file_path)
                globalTrainedModels[label] = onnx

            for key, model in globalTrainedModels.items():
                # print model names to confirm which models are loaded
                print(model.__str__())

            print("ONNX import finished")
        else:
            print("\nStart of LIWC Model Training")

            # create feature pipeline
            features = Features()
            liwcFeaturePipeline = features.createLIWCFeaturePipeline()

            # create list of models with parameters
            # this list will be used for model selection
            modelList = self.createLIWCModels()

            # begin training
            modelTraining = ModelTraining(
                labelsGlobalList=self.config['labelsGlobalList']
            )
            globalBestModels = modelTraining.startModelSelection(
                modelObjList=modelList,
                featurePipeline=liwcFeaturePipeline,
                profileColTraining=profileCol,
            )

            # fully train model in different method of modelTraining
            print("\nFull model training for selected models")
            globalTrainedModels = modelTraining.completeModelTraining(
                modelCollection=globalBestModels,
                featurePipeline=liwcFeaturePipeline,
                profileColTraining=profileCol,
            )

            # only export models if specified
            if writePickleFiles is True:
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/'
                )

                # save models
                for key, model in globalTrainedModels.items():
                    # concatenate file path
                    file_path = Path(
                        file_directory_string +
                        model.labelName +
                        ".pickle"
                    )
                    # call export function for model
                    model.exportModelPickle(
                        file_path
                    )

            # export to ONNX
            if writeONNXModel is True:
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/'
                )

                # save models
                for key, model in globalTrainedModels.items():
                    # concatenate file path
                    file_path = Path(
                        file_directory_string +
                        model.labelName +
                        ".ONNX"
                    )
                    # call export function for model
                    model.exportModelONNX(
                        file_path
                    )

            print("\nEnd of LIWC Model Training\n")

        return
