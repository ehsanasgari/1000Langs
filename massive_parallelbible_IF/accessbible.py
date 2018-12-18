__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"

import codecs
import re
import os
import sys


sys.path.append("../")
from utility.file_utility import FileUtility
import itertools


class AccessBible:
    '''
    This class provide access to 1000s versions of bible in various languages
    '''
    path = '/mounts/data/proj/asgari/superparallelproj/paralleltext/bibles/corpus/'

    def __init__(self, path):
        '''
        :param path: directory of bible corpus
        '''
        self.bible_id_rgx = re.compile('^\s*[0-9]')
        if not os.access(path, os.F_OK):
            print("\nError: Permission denied or could not find the directory of bible corpus!")
            exit()
        else:
            print('Bible directory has been found successfully!')
            self.path = path
            self.all_bible_files = FileUtility.recursive_glob(self.path, '*.txt')
            print('%d bible translations have been found!' % len(self.all_bible_files))

    def get_list_of_all_lang_translations(self):
        '''
        :return: dictionary of lang ==> translations 
        '''
        language_dict = dict()
        for file in self.all_bible_files:
            translation = file.split('/')[-1].split('.')[0].split('-')[-1].replace(' ', '')
            name = file.split('/')[-1].split('-')[0]
            if name not in language_dict:
                language_dict[name] = []
            if translation in language_dict[name]:
                print(name)
            language_dict[name].append(translation)
        return language_dict

    def get_list_of_bible_trans_path_by_lang(self, lang):
        '''
        :param lang: 3letters code of the language
        This function reads translation names and their path e.g.: [[goodnews, path1],...]
        '''
        lang_files = FileUtility.recursive_glob(self.path, lang + '*.txt')
        lang_files_id_address = [[(file.split('/')[-1].split('.')[0].split('-')[-1].replace(' ', '')), file] for file in
                                 lang_files]
        return lang_files_id_address

    def get_bible_corpus_by_lang(self, lang):
        '''
        :param lang: 3letters code of the language
        This function reads the bible verses in a dictionary
        '''
        lang_files_id_address = self.get_list_of_bible_trans_path_by_lang(lang)
        corpus_dict = dict()
        for translation_name, file_address in lang_files_id_address:
            corpus_dict[translation_name] = dict({line.split('\t')[0]: line.split('\t')[1].rstrip() for line in
                                                  codecs.open(file_address, 'r', 'utf-8').readlines() if
                                                  re.search(self.bible_id_rgx, line) and len(
                                                      line.split('\t')[1].rstrip()) > 0})
        return corpus_dict

    def get_bible_corpus_by_path_verses(self, file_address, filter):
        '''
        :param file_address: corpus address
        :param filter: verses to include
        This function reads the new testament verses in a dictionary
        '''

        corpus_dict = dict({line.split('\t')[0]: line.split('\t')[1].rstrip() for line in
                            codecs.open(file_address, 'r', 'utf-8').readlines() if
                            re.search(self.bible_id_rgx, line) and len(
                                line.split('\t')[1].rstrip()) > 0 and line.split('\t')[0] in filter})
        return corpus_dict

    def get_parallel_corpora_by_langtrans_list_filtered(self, languages_translation_dict_list, filter=[], preprocess=str,
                                             verse_include='intersection'):
        '''
        This function get a list of languages and their translations and align them to build a parallel corpora
        for some filtered verses
        :param languages_translation_dict_list: e.g.: {'en':['newliving','treeoflife'],'pes':['newliving', ..]}
        :param filter: filter verses
        :param preprocess: preprocessing function
        :param verse_include: intersection or union
        :return: The output is a dictionary of aligned verses (key is lang_trans) and the common verse ids (with respect
         to the order in the first output)
        '''
        subcorpus = dict()
        common_verses = []
        for lang in languages_translation_dict_list.keys():
            lang_files_id_address = self.get_list_of_bible_trans_path_by_lang(lang)
            for trans, file_address in lang_files_id_address:
                if trans in languages_translation_dict_list[lang]:
                    if len(filter) == 0:
                        subcorpus[lang + '_' + trans] = dict(
                            {line.split('\t')[0]: preprocess(line.split('\t')[1].rstrip()) for line in
                             codecs.open(file_address, 'r', 'utf-8').readlines() if
                             re.search(self.bible_id_rgx, line) and len(
                                 line.split('\t')[1].rstrip()) > 0})
                    else:
                        subcorpus[lang + '_' + trans] = dict(
                            {line.split('\t')[0]: preprocess(line.split('\t')[1].rstrip()) for line in
                             codecs.open(file_address, 'r', 'utf-8').readlines() if
                             re.search(self.bible_id_rgx, line) and len(
                                 line.split('\t')[1].rstrip()) > 0 and (line.split('\t')[0] in filter)})

                    common_verses.append(list(subcorpus[lang + '_' + trans].keys()))

        if verse_include == 'intersection':
            common_verses = list(set.intersection(*map(set, common_verses)))
            common_verses.sort()
            print(' The input translations sharing %d common verse ' % len(common_verses))
            for lang_trans, verse_dic in subcorpus.items():
                ids_to_be_removed = []
                for idx, verse in verse_dic.items():
                    if idx not in common_verses:
                        ids_to_be_removed.append(idx)
                for x in ids_to_be_removed:
                    del subcorpus[lang_trans][x]
        elif verse_include == 'union':
            common_verses = list(set(itertools.chain(*common_verses)))
            print(' The input translations spanning %d common verse ' % len(common_verses))
        # return a dictionary of aligned verses (key is lang_trans) along with the common verses
        return self.get_aligned_corpora_by_common_verses(subcorpus, common_verses), common_verses

    def get_subcorpus_bible_by_lang_trans_filtered(self, lang, trans_l, preprocess=str, filter=[]):
        '''
        This function get a list of languages and their translations and align them to build a parallel corpora
        :param lang: language
        :param trans_l: e.g.: {'en':['newliving','treeoflife'],'pes':['newliving', ..]}
        :param preprocess: function to be applied on the verses
        :param filter: filter verses
        :return: The output is a dictionary of aligned verses (key is lang_trans) and the common verse ids (with respect
         to the order in the first output)
        '''
        lang_files_id_address = self.get_list_of_bible_trans_path_by_lang(lang)
        for trans, file_address in lang_files_id_address:
            if trans == trans_l:
                if len(filter) > 0:
                    return dict({line.split('\t')[0]: preprocess(line.split('\t')[1].rstrip()) for line in
                                 codecs.open(file_address, 'r', 'utf-8').readlines() if
                                 re.search(self.bible_id_rgx, line) and len(
                                     line.split('\t')[1].rstrip()) > 0 and line.split('\t')[0] in filter})
                else:
                    return dict({line.split('\t')[0]: preprocess(line.split('\t')[1].rstrip()) for line in
                                 codecs.open(file_address, 'r', 'utf-8').readlines() if
                                 re.search(self.bible_id_rgx, line) and len(
                                     line.split('\t')[1].rstrip()) > 0})

    def get_langtrans_metadata(self, lang, trans_l):
        '''
        This function returns the metadata
        :param lang: language
        :param trans_l: e.g.: {'en':['newliving','treeoflife'],'pes':['newliving', ..]}
        :param preprocess: function to be applied on the verses
        :return: The output is a dictionary of aligned verses (key is lang_trans) and the common verse ids (with respect
         to the order in the first output)
        '''
        name=''
        url=''
        lang_files_id_address = self.get_list_of_bible_trans_path_by_lang(lang)
        for trans, file_address in lang_files_id_address:
            if trans == trans_l:
                name,url=[''.join(codecs.open(file_address, 'r', 'utf-8').readlines()[x].replace(' ','').replace('\t','').replace('#language_name:','').replace('#URL:','').rstrip()) for x in [0,5]]
        return name,url

    def get_aligned_corpora_by_common_verses(self, subcorpus, common_verses):
        '''
        This function return a dictionary of aligned verses (key is lang_trans)
        :param subcorpus: dict of translations to common verses
        :param common_verse: sorted common verses
        :return:
        '''
        aligned_verses = dict()
        for trans_name in subcorpus.keys():
            aligned_verses[trans_name] = []
            for idx in common_verses:
                if idx in subcorpus[trans_name]:
                    aligned_verses[trans_name].append(subcorpus[trans_name][idx])
                else:
                    aligned_verses[trans_name].append('X'*100)
        return aligned_verses

    @staticmethod
    def produce_lang_alphabet_files(path):
        '''
        :param path:
        :return: produce alphabets and language corpora
        '''
        AB=AccessBible(AccessBible.path)
        langs_sets=AB.get_list_of_all_lang_translations()
        for idx, lang in enumerate(list(langs_sets.keys())):
            print (' '.join([str(idx), lang]))
            lang_corpora=[]
            res=AB.get_bible_corpus_by_lang(lang)
            trans_alph=set()
            alph=codecs.open(path+lang+'.txt','w','utf-8')
            for tr,verse_dict in res.items():
                for k,v in verse_dict.items():
                    trans_alph.update(list(v))
                    lang_corpora.append(v)
                trans_alph=list(trans_alph)
                trans_alph.sort()
                alph.write('\t'.join([tr]+list(trans_alph))+'\n')
                trans_alph=set()
            alph.close()
            f=codecs.open(path+lang+'_corpus.txt','w','utf-8')
            for verse in lang_corpora:
                f.write(verse+'\n')
            f.close()

if __name__ == '__main__':
    AccBible = AccessBible(AccessBible.path)
    newliving = AccBible.get_subcorpus_bible_by_lang_trans_filtered('eng','newliving')
