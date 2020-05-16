class Profile:
    """
    TODO docstring Class Profile
    """

    attributeNameList = [
        'userID',
        'numberWords',
        'numberTweets',
        'language',
        'big5_openness',
        'facet_adventurousness',
        'facet_artistic_interests',
        'facet_emotionality',
        'facet_imagination',
        'facet_intellect',
        'facet_liberalism',
        'big5_conscientiousness',
        'facet_achievement_striving',
        'facet_cautiousness',
        'facet_dutifulness',
        'facet_orderliness',
        'facet_self_discipline',
        'facet_self_efficacy',
        'big5_extraversion',
        'facet_activity_level',
        'facet_assertiveness',
        'facet_cheerfulness',
        'facet_excitement_seeking',
        'facet_friendliness',
        'facet_gregariousness',
        'big5_agreeableness',
        'facet_altruism',
        'facet_cooperation',
        'facet_modesty',
        'facet_morality',
        'facet_sympathy',
        'facet_trust',
        'big5_neuroticism',
        'facet_anger',
        'facet_anxiety',
        'facet_depression',
        'facet_immoderation',
        'facet_self_consciousness',
        'facet_vulnerability',
        'text'
    ]

    def __init__(
        self,
        userID=None,
        text=None,
        numberWords=None,
        numberTweets=None,
        language=None,
        ibmJson=None
    ):
        """
        TODO init func Class Profile
        """

        # initialize attributes even if they are none
        # that way every profile will have all attributes
        for attr in Profile.attributeNameList:
            setattr(self, attr, None)

        # if main attributes are given, save them
        self.userID = userID
        self.text = text
        self.numberWords = numberWords
        self.numberTweets = numberTweets
        self.language = language

        if ibmJson is not None:
            # fill profile variables with ibm json
            self.load_ibm_json(
                ibmJson=ibmJson
            )

        return

    def load_ibm_json(
        self,
        ibmJson,
    ):
        """
        TODO load_ibm_json
        """

        # fill object variables based on IBM json
        for mainTrait in ibmJson['personality']:
            if mainTrait['trait_id'] == 'big5_openness':
                # call function to load trait and facets
                self._load_ibm_openness(mainTrait)

            if mainTrait['trait_id'] == 'big5_conscientiousness':
                # call function to load trait and facets
                self._load_ibm_conscientiousness(mainTrait)

            if mainTrait['trait_id'] == 'big5_extraversion':
                # call function to load trait and facets
                self._load_ibm_extraversion(mainTrait)

            if mainTrait['trait_id'] == 'big5_agreeableness':
                # call function to load trait and facets
                self._load_ibm_agreeableness(mainTrait)

            if mainTrait['trait_id'] == 'big5_neuroticism':
                # call function to load trait and facets
                self._load_ibm_neuroticism(mainTrait)

        return

    def _load_ibm_openness(
        self,
        opennessDict,
    ):
        """
        TODO _load_ibm_openness
        """
        # save main trait
        self.big5_openness = opennessDict['percentile']

        # iterate over children to get facets
        for facet in opennessDict['children']:
            # save each facet
            if facet['trait_id'] == 'facet_adventurousness':
                self.facet_adventurousness = facet['percentile']
            if facet['trait_id'] == 'facet_artistic_interests':
                self.facet_artistic_interests = facet['percentile']
            if facet['trait_id'] == 'facet_emotionality':
                self.facet_emotionality = facet['percentile']
            if facet['trait_id'] == 'facet_imagination':
                self.facet_imagination = facet['percentile']
            if facet['trait_id'] == 'facet_intellect':
                self.facet_intellect = facet['percentile']
            if facet['trait_id'] == 'facet_liberalism':
                self.facet_liberalism = facet['percentile']

        return

    def _load_ibm_conscientiousness(
        self,
        conscientiousnessDict,
    ):
        """
        TODO _load_ibm_conscientiousness
        """
        # save main trait
        self.big5_conscientiousness = conscientiousnessDict['percentile']

        # iterate over children to get facets
        for facet in conscientiousnessDict['children']:
            # save each facet
            if facet['trait_id'] == 'facet_achievement_striving':
                self.facet_achievement_striving = facet['percentile']
            if facet['trait_id'] == 'facet_cautiousness':
                self.facet_cautiousness = facet['percentile']
            if facet['trait_id'] == 'facet_dutifulness':
                self.facet_dutifulness = facet['percentile']
            if facet['trait_id'] == 'facet_orderliness':
                self.facet_orderliness = facet['percentile']
            if facet['trait_id'] == 'facet_self_discipline':
                self.facet_self_discipline = facet['percentile']
            if facet['trait_id'] == 'facet_self_efficacy':
                self.facet_self_efficacy = facet['percentile']

        return

    def _load_ibm_extraversion(
        self,
        extraversionDict,
    ):
        """
        TODO _load_ibm_extraversion
        """
        # save main trait
        self.big5_extraversion = extraversionDict['percentile']

        # iterate over children to get facets
        for facet in extraversionDict['children']:
            # save each facet
            if facet['trait_id'] == 'facet_activity_level':
                self.facet_activity_level = facet['percentile']
            if facet['trait_id'] == 'facet_assertiveness':
                self.facet_assertiveness = facet['percentile']
            if facet['trait_id'] == 'facet_cheerfulness':
                self.facet_cheerfulness = facet['percentile']
            if facet['trait_id'] == 'facet_excitement_seeking':
                self.facet_excitement_seeking = facet['percentile']
            if facet['trait_id'] == 'facet_friendliness':
                self.facet_friendliness = facet['percentile']
            if facet['trait_id'] == 'facet_gregariousness':
                self.facet_gregariousness = facet['percentile']

        return

    def _load_ibm_agreeableness(
        self,
        agreeablenessDict,
    ):
        """
        TODO _load_ibm_agreeableness
        """
        # save main trait
        self.big5_agreeableness = agreeablenessDict['percentile']

        # iterate over children to get facets
        for facet in agreeablenessDict['children']:
            # save each facet
            if facet['trait_id'] == 'facet_altruism':
                self.facet_altruism = facet['percentile']
            if facet['trait_id'] == 'facet_cooperation':
                self.facet_cooperation = facet['percentile']
            if facet['trait_id'] == 'facet_modesty':
                self.facet_modesty = facet['percentile']
            if facet['trait_id'] == 'facet_morality':
                self.facet_morality = facet['percentile']
            if facet['trait_id'] == 'facet_sympathy':
                self.facet_sympathy = facet['percentile']
            if facet['trait_id'] == 'facet_trust':
                self.facet_trust = facet['percentile']

        return

    def _load_ibm_neuroticism(
        self,
        neuroticismDict,
    ):
        """
        TODO _load_ibm_neuroticism
        """
        # save main trait
        self.big5_neuroticism = neuroticismDict['percentile']

        # iterate over children to get facets
        for facet in neuroticismDict['children']:
            # save each facet
            if facet['trait_id'] == 'facet_anger':
                self.facet_anger = facet['percentile']
            if facet['trait_id'] == 'facet_anxiety':
                self.facet_anxiety = facet['percentile']
            if facet['trait_id'] == 'facet_depression':
                self.facet_depression = facet['percentile']
            if facet['trait_id'] == 'facet_immoderation':
                self.facet_immoderation = facet['percentile']
            if facet['trait_id'] == 'facet_self_consciousness':
                self.facet_self_consciousness = facet['percentile']
            if facet['trait_id'] == 'facet_vulnerability':
                self.facet_vulnerability = facet['percentile']

        return
