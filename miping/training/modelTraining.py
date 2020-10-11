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
    Wrapper class for all model training functions.
    """

    def __init__(
        self,
        labelsGlobalList,
        crossValidationIterations=10,
        n_jobs=1,
        # e.g. neg_mean_absolute_error MAE or
        # neg_root_mean_squared_error RMSE
        scoringFunc='neg_root_mean_squared_error',
        printIntermediateResults=True,
        printCoefficients=False,
    ):
        """
        Initialize values for model training.

        Parameters
        ----------
        labelsGlobalList : list, default=None, required
            List of dimensions to predict (e.g. Big Five).
        crossValidationIterations : integer, default=10
            Number of cross validation iterations.
        n_jobs : integer, default=1
            Number of prallel jobs in sklearn.
            n_jobs=-1 -> parallelization. Does not always work.
            E.g. SVM throws warnings.
        scoringFunc : string, default='neg_root_mean_squared_error'
            Which scoring function should be chosen for selecting
            the best model. Should be sklearn function. Since sklearn
            follows "higher = better". Error scores are negative.
        printIntermediateResults : boolean, default=True
            Print intermediate results, such as scores.
        printCoefficients : boolean, default=False
            Print model coefficients and kernel parameters of trained models.
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
        Extract values for one specific labelName
        labels are the percentages value to predict
        e.g. for Extraversion value.

        Parameters
        ----------
        profileList : list, default=None, required
            List of profiles to extract labels from.
        labelName : string, default=None, required
            Label to extract from profiles.

        Returns
        -------
        labels : list
            Numeric values used for training and prediction.
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
        Return best model from grid search and do cross validation.

        A grid search is performed with the given parameters.
        The best model selected and a cross validation with
        this model performed. Scores will be printed to console.
        Duration of process is printed.

        Parameters
        ----------
        model : modelBase.model, default=None, required
            Model from sklearn to train.
        gridSearchParams : dict, default=None, required
            Dictionary with parameters for grid search.
        labels : list, default=None, required
            Numeric values as prediction target.
        features : numpy.array, default=None, required
            Numeric features to predict from.

        Returns
        -------grid_model.best_score_, bestModel, bestParams
        grid_model.best_score_ : dict
            Dictionary with scores of best model.
        bestModel : modelBase.model
            Best performing model during gridsearch.
        bestParams : dict
            Parameters of best performing model.
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
            if hasattr(bestModel, 'kernel_'):
                # gaussian proccesses have kernel parameters
                print(
                    "Kernel parameters: " +
                    str(bestModel.kernel_)
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
        Does cross validation for given model in modelBase.
        Calculates MAE, MSE, RMSE, correlations and R2.
        Prints results and saves in modelBase.

        Parameters
        ----------
        modelBase : modelBase, default=None, required
            ModelBase class containing the model.
        labels : list, default=None, required
            Numeric values as prediction target.
        features : numpy.array, default=None, required
            Numeric features to predict from.
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
        for key in scoring.keys():
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
        saveFeatures=False,
        precalculatedFeatures=None,
    ):
        """
        Identify best model for each dimension.

        First, features are calculated. The model selection is done
        for each dimension (label). Labels are extracted and for each
        model in modelObjList grid search is performed.
        Then best model is identified for this dimension and added to
        globalBestModels.
        Additional scores are provided via cross validation.

        Parameters
        ----------
        modelObjList : list, default=None, required
            List of models to select from.
        featurePipeline : Pipeline, default=None, required
            Created feature pipeline to use.
        profileColTraining : ProfileCollection, default=None, required
            ProfileCollection to generate features and extract labels from.
        saveFeatures : boolean, default=False
            To save time feature calculation step can be saved and
            exported in caller function.
        precalculatedFeatures : numpy array, default=None
            If passed, those features are used and no feature calculation
            takes place.

        Returns
        -------
        globalBestModels : dict
            Dictionary with best model for each label to predict.
        """
        profileList = profileColTraining.profileList

        if precalculatedFeatures is None:
            # calculate features once
            print("Calculating features")
            features = featurePipeline.fit_transform(profileList)
        else:
            print("Features from passed variable")
            features = precalculatedFeatures

        if saveFeatures is True:
            self.features = features

        print("Feature shape: " + str(features.shape))
        self.features = features

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
                for score in scoreStatistics[modelType].values():
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
        saveFeatures=False,
        precalculatedFeatures=None,
    ):
        """
        Fully train models in modelCollection.

        Features are calculated, then for each dimension model is
        fully trained and saved back in collection.

        Parameters
        ----------
        modelCollection : dict, default=None, required
            Dictionary of best models to fully train.
        featurePipeline : Pipeline, default=None, required
            Created feature pipeline to use.
        profileColTraining : ProfileCollection, default=None, required
            ProfileCollection to generate features and extract labels from.
        saveFeatures : boolean, default=False
            To save time feature calculation step can be saved and
            exported in caller function.
        precalculatedFeatures : numpy array, default=None
            If passed, those features are used and no feature calculation
            takes place.

        Returns
        -------
        modelCollection : dict
            Collection contains now fully trained models.
        """
        profileList = profileColTraining.profileList

        if precalculatedFeatures is None:
            # calculate features once
            print("Calculating features for complete training")
            features = featurePipeline.fit_transform(profileList)
        else:
            print("Features from passed variable")
            features = precalculatedFeatures

        if saveFeatures is True:
            self.features = features

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
        Helps when saving scores to intialize
        dictionary.
        nested arrays
        https://stackoverflow.com/questions/13687924/
        setting-a-value-in-a-nested-python-dictionary-
        given-a-list-of-indices-and-value
        """
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})
        dic[keys[-1]] = value
