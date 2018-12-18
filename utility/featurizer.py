__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"


from sklearn.feature_extraction.text import TfidfVectorizer

class TextFeature(object):
    '''
    This class is to create feature matrix
    '''
    def __init__(self, corpus, analyzer='word', ngram=(1,1), idf=False, norm=None, binary=False):
        tfm = TfidfVectorizer(use_idf=idf, analyzer=analyzer, tokenizer=str.split, ngram_range=ngram, norm=norm, stop_words=[], lowercase=False, binary=binary)
        self.tf_vec = tfm.fit_transform(corpus)
        self.feature_names = tfm.get_feature_names()
