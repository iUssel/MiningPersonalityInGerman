import datetime
import numpy as np

from ..models.modelBase import ModelBase

from warnings import simplefilter

from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_validate


class ModelTraining:
    """
    TODO docstring Class ModelTraining
    """

    def __init__(
        self,
        labelsGlobalList,
        crossValidationIterations=10,
        n_jobs=1,  # TODO evtl. auf -1
        # e.g. neg_mean_absolute_error MAE or
        # neg_root_mean_squared_error RMSE
        scoringFunc='neg_root_mean_squared_error',
        printIntermediateResults=True,
        printCoefficients=False,
    ):
        """
        TODO init func Class ModelTraining
        labelsGlobalList -> values to predict
        n_jobs=-1 -> parallelization
        """
        # save list of labels to predict
        # one model for each label will be calculated
        self.labelsGlobalList = labelsGlobalList

        # number of iterations during cross validations
        self.crossValidationIterations = crossValidationIterations

        # 1 if no parallelization, -1 all CPU cores
        self.n_jobs = n_jobs

        # scoring function used during cross validation
        self.scoringFunc = scoringFunc

        # to keep the terminal output clean, prints can
        # be minimized, showing only most relevant prints
        self.printIntermediateResults = printIntermediateResults

        # some model's have coefficients that are
        # set during training and might be of interest
        self.printCoefficients = printCoefficients

        return

    def extractLabels(
        self,
        profileList,
        labelName,
    ):
        """
        TODO func extractLabels
        extract values for one specific labelName
        labels are the percentages value to predict
        e.g. for Extraversion value
        """
        # initialize return variable
        labels = []

        # loop over profile collection
        for profile in profileList:
            value = getattr(profile, labelName)
            labels.append(np.float(value))

        return labels

    def crossvalidateModel(
        self,
        model,
        gridSearchParams,
        labels,
        features
    ):
        """
        TODO func doc crossvalidateModel
        """

        # ignore terminated early warning
        # for SVMs we set a hard limit for max iterations
        # and it would print this warning once the iterations
        # are reached.
        # somehow a bug in scikit prevents ignoring
        # when running job in parallel
        simplefilter("ignore", category=ConvergenceWarning)

        # save start time, for runtime calculation
        startTime = datetime.datetime.now()

        # set up cross validation with params
        grid_model = GridSearchCV(
            model,
            gridSearchParams,
            cv=self.crossValidationIterations,
            n_jobs=self.n_jobs,
            scoring=self.scoringFunc  # we usually use RMSE
        )

        # number of datasets available
        n = len(labels)

        # actually do grid search
        grid_model = grid_model.fit(features[:n], labels[:n])

        if self.printIntermediateResults is True:
            print("best score: " + str(grid_model.best_score_))
        bestParams = {}
        for param_name in sorted(gridSearchParams.keys()):
            bestParams[param_name] = grid_model.best_params_[param_name]
            if self.printIntermediateResults is True:
                print(
                    "%s: %r" %
                    (param_name, grid_model.best_params_[param_name])
                )

        # set classifier to best classifier found by GridSearchCV
        bestModel = grid_model.best_estimator_

        # cross validation
        scores = cross_val_score(
            bestModel,
            features,
            labels,
            cv=self.crossValidationIterations,
            n_jobs=self.n_jobs,
            scoring=self.scoringFunc
        )
        if self.printIntermediateResults is True:
            print(
                self.scoringFunc +
                " Score: %0.4f (+/- %0.4f)" %
                (scores.mean(), scores.std() * 2)
            )
        if self.printCoefficients is True:
            if hasattr(bestModel, 'coef_'):
                # some models provide coefficients
                # that are set during training
                print(
                    "Model's coefficients: " +
                    str(bestModel.coef_)
                )

        endTime = datetime.datetime.now()
        runTime = endTime - startTime
        if self.printIntermediateResults is True:
            print("Duration: " + str(runTime))

        return grid_model.best_score_, bestModel, bestParams

    def provideScores(
        self,
        modelBase,
        labels,
        features
    ):
        """
        TODO func doc provideScores
        MAE, MSE, RMSE, correlations and R2
        """
        # get actual estimator from object
        model = modelBase.model
        # summarize all metrics
        scoring = {
            'negMAE': 'neg_mean_absolute_error',
            'negMSE': 'neg_mean_squared_error',
            'negRMSE': 'neg_root_mean_squared_error',
            'R2': 'r2',
        }

        # cross validation to estimate scores again
        cv_results = cross_validate(
            model,
            features,
            labels,
            cv=self.crossValidationIterations,
            n_jobs=self.n_jobs,
            scoring=scoring
        )

        scores_to_save = {}

        # Printing scores for each model
        for i, key in enumerate(scoring):
            # get results, these are prefixed with test_
            key_value = ('test_' + str(key))
            scores = cv_results[key_value]
            values = "%0.4f (+/- %0.4f)" % (scores.mean(), scores.std() * 2)
            if self.printIntermediateResults is True:
                print(
                    str(key) + ": " +
                    str(values)
                )
            # save scores to save it later in model object
            scores_to_save[key] = values

        # save scores in model object
        modelBase.scores = scores_to_save

        return

    def startModelSelection(
        self,
        modelObjList,
        featurePipeline,
        profileColTraining,
    ):
        """
        TODO doc func startModelSelection
        take modellist and do training
        """

        # calculate features once
        print("Calculating features")
        profileList = profileColTraining.profileList
        features = featurePipeline.fit_transform(profileList)

        print("Feature shape: " + str(features.shape))

        globalBestModels = {}
        scoreStatistics = {}

        # do this whole process for each label
        # (e.g. big dimensions or big 5 facets)
        for labelName in self.labelsGlobalList:
            print(
                "\nModel Selection currently for label: " +
                str(labelName)
            )
            # extract labels for prediction (e.g. values for Extraversion)
            labels = self.extractLabels(
                profileList=profileList,
                labelName=labelName
            )

            labelBestModels = {}

            # for each model in model list, we will perform grid search
            for modelObj in modelObjList:
                # get model
                currentModel = modelObj.getModel()
                currentGridParams = modelObj.gridSearchParams
                print('\nCurrently at model: ' + modelObj.modelName)
                # do crossvalidation for this model

                best_score, bestModel, bestParams = self.crossvalidateModel(
                    model=currentModel,
                    gridSearchParams=currentGridParams,
                    labels=labels,
                    features=features,
                )
                # save best model as object in dict, to select from
                # after all have been evaluated
                localModel = ModelBase(
                    labelName=labelName,
                    modelName=modelObj.modelName,
                    model=bestModel,
                    params=bestParams,
                    scores=best_score,
                    gridSearchParams=None,
                )
                labelBestModels[modelObj.modelName] = localModel
                # save score in dict, to evalute each model type
                # at the end of the function
                self._nested_set(
                    scoreStatistics,
                    [modelObj.modelName, labelName],
                    best_score
                )

            # select best model and its params by taking entry
            # with highest score
            bestModelName = max(
                labelBestModels.keys(),
                key=(lambda k: labelBestModels[k].scores)
            )
            # save it for this label in dict
            globalBestModels[labelName] = labelBestModels[bestModelName]

            # print model name
            print(
                "\nBest model for " +
                labelName +
                " is " +
                globalBestModels[labelName].modelName
            )

            # provide MAE, MSE, RMSE, correlations and R2
            # for comparison reasons
            self.provideScores(
                globalBestModels[labelName],
                labels,
                features
            )

        # for comparison identify model, that on average performs
        # best over all labels
        # meaning good scores in all dimensions for this model type
        # helps with model selection and avoid overfitting
        if self.printIntermediateResults is True:
            print(
                "\nOverall average performance " +
                "(might help with model selection):"
            )
            meanScores = {}
            for modelType in scoreStatistics:
                scores = 0
                counter = 0
                for label, score in scoreStatistics[modelType].items():
                    scores = scores + float(score)
                    counter = counter + 1
                mean = scores / counter
                meanScores[modelType] = mean
                print(
                    "Mean score over all dimensions for model type " +
                    str(modelType) +
                    " is :" +
                    str(mean)
                )
            # best mean score
            meanBest = max(
                meanScores.keys(),
                key=(lambda k: meanScores[k])
            )
            print("Mean best is " + str(meanBest))

        return globalBestModels

    def completeModelTraining(
        self,
        modelCollection,
        featurePipeline,
        profileColTraining,
    ):
        """
        TODO doc func completeModelTraining
        take modellist and do training
        """

        # calculate features once
        print("Calculating features for complete training")
        profileList = profileColTraining.profileList
        features = featurePipeline.fit_transform(profileList)

        for labelName in self.labelsGlobalList:
            print(
                "Full Model Training currently for label: " +
                str(labelName)
            )
            # extract labels for prediction (e.g. values for Extraversion)
            labels = self.extractLabels(
                profileList=profileList,
                labelName=labelName
            )

            # select the model we previously evaluated for this trait
            baseModel = modelCollection[labelName]
            model = baseModel.model

            # for each model, we will fully train the model
            model.fit(features, labels)

            # save model back in object
            baseModel.model = model
            # back into collection
            modelCollection[labelName] = baseModel

        return modelCollection

    def _nested_set(
        self,
        dic,
        keys,
        value
    ):
        """
        TODO doc string _nested_set
        nested arrays
        https://stackoverflow.com/questions/13687924/
        setting-a-value-in-a-nested-python-dictionary-
        given-a-list-of-indices-and-value
        """
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})
        dic[keys[-1]] = value
