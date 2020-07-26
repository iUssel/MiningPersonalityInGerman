import miping.models as mipingModels

from pathlib import Path
import numpy as np

from miping.training.features import Features
from miping.training.modelTraining import ModelTraining
from miping.models.profileCollection import ProfileCollection
from miping.interfaces.helper import Helper


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

    def createModels(
        self,
        step='LIWC',
    ):
        """
        TODO docstring createModels

        returns modelList
        """

        if step == 'LIWC':
            configString = 'liwcModelSelection'
        elif step == 'glove':
            # glove
            configString = 'gloveModelSelection'
        else:
            raise Exception("Unknown step in createModels")

        # this will contain all model instances that we want to train
        modelList = []

        # get model names from config
        # list of models to be created
        # not safe, but this is
        loadModels = []
        for model in self.modelConfig[configString]:
            loadModels.append(model)

        # gridsearch parameters from config
        gridParams = self.modelConfig[configString]

        # create model instances with grid search parameters
        # loaded from config
        for loadModel in loadModels:
            # load config for this model
            params = gridParams[loadModel]
            # check if model class exists
            if hasattr(mipingModels, loadModel) is False:
                exceptString = (
                    "Model " +
                    str(loadModel) +
                    " does not exist in MiPInG." +
                    "Check config_models.yml."
                )
                raise Exception(exceptString)
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
            modelList = self.createModels(step='LIWC')

            # begin training
            modelTraining = ModelTraining(
                labelsGlobalList=self.config['labelsGlobalList'],
                printIntermediateResults=self.config['printDetailResults']
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
                # create new line
                print("")
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
                # create new line
                print("")
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
                    # since it's LIWC model, 93 is input dimension
                    model.exportModelONNX(
                        path=file_path,
                        numDim=93,
                        inputName='liwc_input',
                    )

            print("\nEnd of LIWC Model Training\n")

        return globalTrainedModels

    def predictPersonalitiesLIWC(
        self,
        profileCol,
        country,
        globalLIWCModels,
        ibmList,
        readFiles=False,
        writeFiles=False,
    ):
        """
        TODO predictPersonalities
        ibmList list of countries we already got profiles
        """
        if writeFiles is True and readFiles is True:
            raise Exception(
                "readFiles and writeFiles cannot be True at the same time."
            )

        returnProfileCol = ProfileCollection()

        if readFiles is True:
            print("\nReading files for predict personalities with LIWC")
            print(
                "Loading for country: " +
                country
            )

            # path for saved profiles
            file_directory_string = (
                'data/07' +
                country +
                'full_profiles.csv'
            )
            file_path = Path(file_directory_string)

            returnProfileCol.read_profile_list_file(
                full_path=file_path
            )

            print("Files successfully loaded")
        else:
            print("\nBegin predicting personalities with LIWC")
            print(
                "Country: " +
                country
            )

            # check if already predicted via IBM
            if country in ibmList:
                print("Personalities already retrieved via IBM")
                # just return passed collection
                returnProfileCol = profileCol

            else:
                # for the remaining countries do prediction

                # create feature pipeline
                features = Features()
                liwcFeaturePipeline = features.createLIWCFeaturePipeline()
                profileList = profileCol.profileList
                features = liwcFeaturePipeline.fit_transform(profileList)
                print(
                    "Feature shape " +
                    str(features.shape)
                )

                # initialize progress bar
                helper = Helper()
                numProfiles = len(profileCol.profileList)
                helper.printProgressBar(
                    0,
                    numProfiles,
                    prefix='Progress:',
                    suffix='Complete',
                    length=50
                )

                # iterate over all profiles
                # and enrich profiles with prediction
                for num, profile in enumerate(profileCol.profileList):
                    # we just take the row with this profile's features
                    singleFeature = np.array([features[num]])
                    # for each dimension use respective model
                    for dimension, modelBase in globalLIWCModels.items():
                        profile = self.predict_profile(
                            profile=profile,
                            features=singleFeature,
                            dimension=dimension,
                            model=modelBase.model
                        )

                    # add filled profile to collection
                    returnProfileCol.add_profile(profile)

                    # Update Progress Bar
                    helper.printProgressBar(
                        num + 1,
                        numProfiles,
                        prefix='Progress:',
                        suffix='Complete',
                        length=50
                    )

            # only write file if specified
            if writeFiles is True:
                # path for saving profileCollection
                file_directory_string = (
                    'data/07' +
                    country +
                    'full_profiles.csv'
                )
                file_path = Path(file_directory_string)

                returnProfileCol.write_profile_list_file(
                    full_path=file_path
                )
            print("End predicting personalities")

        return returnProfileCol

    def predict_profile(
        self,
        profile,
        features,
        dimension,
        model,
    ):
        """
        TODO doc predict_profile
        """

        result = model.predict(features)
        setattr(profile, dimension, float(result))

        return profile

    def doGloVeModelTraining(
        self,
        profileCol,
        writePickleFiles=False,
        readPickleFiles=False,
        writeONNXModel=False,
        readONNXModel=False,
    ):
        """
        TODO doGloVeModelTraining
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
            print("\nReading files for GloVe model training from pickle")
            # load models in this dict
            globalTrainedModels = {}
            # load models (one for each label (big 5 dimension))
            for label in self.config['labelsGlobalList']:
                # path for saved trained models
                file_directory_string = (
                    'data/trainedModels/glove'
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
            print("\nReading files for GloVe model training from ONNX")
            # load models in this dict
            globalTrainedModels = {}
            # load models (one for each label (big 5 dimension))
            for label in self.config['labelsGlobalList']:
                # path for saved trained models
                file_directory_string = (
                    'data/trainedModels/glove'
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
            print("\nStart of GloVe Model Training")

            # path for GloVe vectors
            file_path = Path(
                'data/glove/glove.db'
            )
            # create feature pipeline
            features = Features()
            gloveFeaturePipeline = features.createGloVeFeaturePipeline(
                glovePath=file_path,
                dataBaseMode=True
            )

            # create list of models with parameters
            # this list will be used for model selection
            modelList = self.createModels(step='glove')

            # begin training
            modelTraining = ModelTraining(
                labelsGlobalList=self.config['labelsGlobalList'],
                printIntermediateResults=self.config['printDetailResults']
            )
            globalBestGloVeModels = modelTraining.startModelSelection(
                modelObjList=modelList,
                featurePipeline=gloveFeaturePipeline,
                profileColTraining=profileCol,
            )

            # fully train model in different method of modelTraining
            print("\nFull model training for selected models")
            globalTrainedModels = modelTraining.completeModelTraining(
                modelCollection=globalBestGloVeModels,
                featurePipeline=gloveFeaturePipeline,
                profileColTraining=profileCol,
            )

            # TODO word coverage analysis
            print(features.coverageStatistics)

            # only export models if specified
            if writePickleFiles is True:
                # create new line
                print("")
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/glove'
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
                # create new line
                print("")
                # path for saving trained models
                file_directory_string = (
                    'data/trainedModels/glove'
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
                    # since it's GloVe model, 900 is input dimension
                    model.exportModelONNX(
                        path=file_path,
                        numDim=900,
                        inputName='glove_input',
                    )

            print("\nEnd of GloVe Model Training\n")

        return globalTrainedModels
