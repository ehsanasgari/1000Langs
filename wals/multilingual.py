# -*- encoding: utf-8 -*-
__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"
import codecs
import itertools
import string


class MultiLingualUtility(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.data_path='/mounts/data/proj/asgari/github_repos/superpivot/wals/wals_data/'
        self._initLanguageCodes()
        self._initLanguageProperties()

    def _initLanguageCodes(self):
        self.code2lang = dict(itertools.chain(
            *[[(l.split('\t')[0], lang) for lang in l.strip().split('\t')[1].split(';')] for l in
              codecs.open(self.data_path+"language_codes.csv", "r", "utf-8").readlines()]))
        self.code2lang.update( dict([(l.split()[0],' '.join(l.split()[1:-2])) for l in
              codecs.open(self.data_path+"language_meta.txt", "r", "utf-8").readlines()[1::]]))

        self.lang2code = dict(itertools.chain(
            *[[(lang, l.split('\t')[0]) for lang in l.strip().split('\t')[1].split(';')] for l in
              codecs.open(self.data_path+"language_codes.csv", "r", "utf-8").readlines()]))

    def _initLanguageProperties(self):
        lines = [l.strip().translate(string.punctuation) for l in codecs.open(
            self.data_path+'language.csv', 'r',
            'utf-8').readlines()]
        self._lang_prop = dict()
        self._attr = [attr.replace(' ', '_') for attr in lines[0].split(',')]

        for line in lines[1::]:
            parts = line.split(',')
            if not parts[1].rstrip() == '':
                if parts[1] in self._lang_prop:
                    self._lang_prop[parts[1]].append(parts)
                else:
                    self._lang_prop[parts[1]] = [parts]
            if not parts[3].rstrip() == '':
                if parts[3] in self._lang_prop:
                        self._lang_prop[parts[3]].append(parts)
                else:
                    self._lang_prop[parts[3]] = [parts]

    def getProperty(self, lang, prop):
        '''
            wals_code
            iso_code
            glottocode
            Name
            latitude
            longitude
            genus
            family
            macroarea
            countrycodes
            1A_Consonant_Inventories
            2A_Vowel_Quality_Inventories
            3A_Consonant-Vowel_Ratio
            4A_Voicing_in_Plosives_and_Fricatives
            5A_Voicing_and_Gaps_in_Plosive_Systems
            6A_Uvular_Consonants
            7A_Glottalized_Consonants
            8A_Lateral_Consonants
            9A_The_Velar_Nasal
            10A_Vowel_Nasalization
            11A_Front_Rounded_Vowels
            12A_Syllable_Structure
            13A_Tone
            14A_Fixed_Stress_Locations
            15A_Weight-Sensitive_Stress
            16A_Weight_Factors_in_Weight-Sensitive_Stress_Systems
            17A_Rhythm_Types
            18A_Absence_of_Common_Consonants
            19A_Presence_of_Uncommon_Consonants
            20A_Fusion_of_Selected_Inflectional_Formatives
            21A_Exponence_of_Selected_Inflectional_Formatives
            22A_Inflectional_Synthesis_of_the_Verb
            23A_Locus_of_Marking_in_the_Clause
            24A_Locus_of_Marking_in_Possessive_Noun_Phrases
            25A_Locus_of_Marking:_Whole-language_Typology
            26A_Prefixing_vs._Suffixing_in_Inflectional_Morphology
            27A_Reduplication
            28A_Case_Syncretism
            29A_Syncretism_in_Verbal_Person/Number_Marking
            30A_Number_of_Genders
            31A_Sex-based_and_Non-sex-based_Gender_Systems
            32A_Systems_of_Gender_Assignment
            33A_Coding_of_Nominal_Plurality
            34A_Occurrence_of_Nominal_Plurality
            35A_Plurality_in_Independent_Personal_Pronouns
            36A_The_Associative_Plural
            37A_Definite_Articles
            38A_Indefinite_Articles
            39A_Inclusive/Exclusive_Distinction_in_Independent_Pronouns
            40A_Inclusive/Exclusive_Distinction_in_Verbal_Inflection
            41A_Distance_Contrasts_in_Demonstratives
            42A_Pronominal_and_Adnominal_Demonstratives
            43A_Third_Person_Pronouns_and_Demonstratives
            44A_Gender_Distinctions_in_Independent_Personal_Pronouns
            45A_Politeness_Distinctions_in_Pronouns
            46A_Indefinite_Pronouns
            47A_Intensifiers_and_Reflexive_Pronouns
            48A_Person_Marking_on_Adpositions
            49A_Number_of_Cases
            50A_Asymmetrical_Case-Marking
            51A_Position_of_Case_Affixes
            52A_Comitatives_and_Instrumentals
            53A_Ordinal_Numerals
            54A_Distributive_Numerals
            55A_Numeral_Classifiers
            56A_Conjunctions_and_Universal_Quantifiers
            57A_Position_of_Pronominal_Possessive_Affixes
            58A_Obligatory_Possessive_Inflection
            59A_Possessive_Classification
            "60A_Genitives
            _Adjectives_and_Relative_Clauses"
            61A_Adjectives_without_Nouns
            62A_Action_Nominal_Constructions
            63A_Noun_Phrase_Conjunction
            64A_Nominal_and_Verbal_Conjunction
            65A_Perfective/Imperfective_Aspect
            66A_The_Past_Tense
            67A_The_Future_Tense
            68A_The_Perfect
            69A_Position_of_Tense-Aspect_Affixes
            70A_The_Morphological_Imperative
            71A_The_Prohibitive
            72A_Imperative-Hortative_Systems
            73A_The_Optative
            74A_Situational_Possibility
            75A_Epistemic_Possibility
            76A_Overlap_between_Situational_and_Epistemic_Modal_Marking
            77A_Semantic_Distinctions_of_Evidentiality
            78A_Coding_of_Evidentiality
            79A_Suppletion_According_to_Tense_and_Aspect
            80A_Verbal_Number_and_Suppletion
            "81A_Order_of_Subject
            _Object_and_Verb"
            82A_Order_of_Subject_and_Verb
            83A_Order_of_Object_and_Verb
            "84A_Order_of_Object
            _Oblique
            _and_Verb"
            85A_Order_of_Adposition_and_Noun_Phrase
            86A_Order_of_Genitive_and_Noun
            87A_Order_of_Adjective_and_Noun
            88A_Order_of_Demonstrative_and_Noun
            89A_Order_of_Numeral_and_Noun
            90A_Order_of_Relative_Clause_and_Noun
            91A_Order_of_Degree_Word_and_Adjective
            92A_Position_of_Polar_Question_Particles
            93A_Position_of_Interrogative_Phrases_in_Content_Questions
            94A_Order_of_Adverbial_Subordinator_and_Clause
            95A_Relationship_between_the_Order_of_Object_and_Verb_and_the_Order_of_Adposition_and_Noun_Phrase
            96A_Relationship_between_the_Order_of_Object_and_Verb_and_the_Order_of_Relative_Clause_and_Noun
            97A_Relationship_between_the_Order_of_Object_and_Verb_and_the_Order_of_Adjective_and_Noun
            98A_Alignment_of_Case_Marking_of_Full_Noun_Phrases
            99A_Alignment_of_Case_Marking_of_Pronouns
            100A_Alignment_of_Verbal_Person_Marking
            101A_Expression_of_Pronominal_Subjects
            102A_Verbal_Person_Marking
            103A_Third_Person_Zero_of_Verbal_Person_Marking
            104A_Order_of_Person_Markers_on_the_Verb
            105A_Ditransitive_Constructions:_The_Verb_'Give'
            106A_Reciprocal_Constructions
            107A_Passive_Constructions
            108A_Antipassive_Constructions
            109A_Applicative_Constructions
            110A_Periphrastic_Causative_Constructions
            111A_Nonperiphrastic_Causative_Constructions
            112A_Negative_Morphemes
            113A_Symmetric_and_Asymmetric_Standard_Negation
            114A_Subtypes_of_Asymmetric_Standard_Negation
            115A_Negative_Indefinite_Pronouns_and_Predicate_Negation
            116A_Polar_Questions
            117A_Predicative_Possession
            118A_Predicative_Adjectives
            119A_Nominal_and_Locational_Predication
            120A_Zero_Copula_for_Predicate_Nominals
            121A_Comparative_Constructions
            122A_Relativization_on_Subjects
            123A_Relativization_on_Obliques
            124A_'Want'_Complement_Subjects
            125A_Purpose_Clauses
            126A_'When'_Clauses
            127A_Reason_Clauses
            128A_Utterance_Complement_Clauses
            129A_Hand_and_Arm
            130A_Finger_and_Hand
            131A_Numeral_Bases
            132A_Number_of_Non-Derived_Basic_Colour_Categories
            133A_Number_of_Basic_Colour_Categories
            134A_Green_and_Blue
            135A_Red_and_Yellow
            136A_M-T_Pronouns
            137A_N-M_Pronouns
            138A_Tea
            139A_Irregular_Negatives_in_Sign_Languages
            140A_Question_Particles_in_Sign_Languages
            141A_Writing_Systems
            142A_Para-Linguistic_Usages_of_Clicks
            143F_Postverbal_Negative_Morphemes
            90B_Prenominal_relative_clauses
            144Y_The_Position_of_Negative_Morphemes_in_Object-Initial_Languages
            90C_Postnominal_relative_clauses
            144P_NegSOV_Order
            144J_SVNegO_Order
            144N_Obligatory_Double_Negation_in_SOV_languages
            144S_SOVNeg_Order
            144X_Verb-Initial_with_Clause-Final_Negative
            "144A_Position_of_Negative_Word_With_Respect_to_Subject
            _Object
            _and_Verb"
            90G_Double-headed_relative_clauses
            90E_Correlative_relative_clauses
            144V_Verb-Initial_with_Preverbal_Negative
            144I_SNegVO_Order
            144R_SONegV_Order
            143B_Obligatory_Double_Negation
            144M_Multiple_Negative_Constructions_in_SOV_Languages
            144U_Double_negation_in_verb-initial_languages
            144G_Optional_Double_Negation_in_SVO_languages
            144K_SVONeg_Order
            144B_Position_of_negative_words_relative_to_beginning_and_end_of_clause_and_with_respect_to_adjacency_to_verb
            144F_Obligatory_Double_Negation_in_SVO_languages
            90D_Internally-headed_relative_clauses
            144E_Multiple_Negative_Constructions_in_SVO_Languages
            144D_The_Position_of_Negative_Morphemes_in_SVO_Languages
            "81B_Languages_with_two_Dominant_Orders_of_Subject
            _Object
            _and_Verb"
            143E_Preverbal_Negative_Morphemes
            143C_Optional_Double_Negation
            90F_Adjoined_relative_clauses
            143A_Order_of_Negative_Morpheme_and_Verb
            144W_Verb-Initial_with_Negative_that_is_Immediately_Postverbal_or_between_Subject_and_Object
            144O_Optional_Double_Negation_in_SOV_languages
            144Q_SNegOV_Order
            144L_The_Position_of_Negative_Morphemes_in_SOV_Languages
            144H_NegSVO_Order
            144C_Languages_with_different_word_order_in_negative_clauses
            144T_The_Position_of_Negative_Morphemes_in_Verb-Initial_Languages
            143G_Minor_morphological_means_of_signaling_negation
            143D_Optional_Triple_Negation
            39B_Inclusive/Exclusive_Forms_in_Pama-Nyungan
            137B_M_in_Second_Person_Singular
            136B_M_in_First_Person_Singular
            109B_Other_Roles_of_Applied_Objects
            10B_Nasal_Vowels_in_West_Africa
            25B_Zero_Marking_of_A_and_P_Arguments
            21B_Exponence_of_Tense-Aspect-Mood_Inflection
            108B_Productivity_of_the_Antipassive_Construction
            130B_Cultural_Categories_of_Languages_with_Identity_of_'Finger'_and_'Hand'
            58B_Number_of_Possessive_Nouns
            79B_Suppletion_in_Imperatives_and_Hortatives
        '''
        try:
            i = self._attr.index(prop)
            if lang in self._lang_prop:
                return list(set([l[i] for l in self._lang_prop[lang]]))
            else:
                print(lang + ' Language do not exist in this database!')
                return None
        except:
            print('Such an attribute does not exist')
            return None


if __name__ == '__main__':
    ML = MultiLingualUtility()
    print(ML.getProperty('fra','genus'))
    # name2three=dict()
    # for l in open('wlas/google_trans_langs','r').readlines():
    #     l=l.strip()
    #     if l in ML._lang_prop:
    #         name2three[l]=ML.getProperty(l, 'iso_code')[0]
    # print (','.join(["'"+name+"':'"+name2three[name]+"'" for name in name2three.keys()]))
    # name2two=dict()
    # for l in open('wlas/language_codes.csv','r').readlines():
    #         two,name=l.split()
    #         if ';' in name:
    #             names=name.split(';')
    #             for name in names:
    #                 name2two[name]=two
    #         else:
    #             name2two[name]=two
    # common_names = list(set(name2two.keys()).intersection(name2three))
    # print (len(common_names))
    #
    # print (','.join(["'"+name2three[name]+"':'"+name2two[name]+"'" for name in common_names]))

