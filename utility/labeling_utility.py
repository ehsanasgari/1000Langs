import sys

sys.path.append('../')
import numpy as np
from keras.preprocessing.text import Tokenizer
from collections import Counter
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from gensim.models import KeyedVectors
from keras.layers import Embedding
from utility.file_utility import FileUtility
from utility.list_set_util import argsort

np.random.seed(7)


class LabelingData(object):
    def __init__(self, train_file, test_file):
        print('Labeling utility object created..')
        ## read train ##
        self.X_train, self.y_train, self.train_lengths = LabelingData.labeling_file_reader(train_file)
        ## read test##
        self.X_test, self.y_test , self.test_lengths= LabelingData.labeling_file_reader(test_file)
        ## data loading
        self.load_data()

    def load_data(self):
        words = list(set([elem for sublist in (self.X_train + self.X_test) for elem in sublist]))
        self.vocab_size = len(words) + 2  # because of <UNK> and <PAD> pseudo words
        self.n_classes = len(set([elem for sublist in (self.y_train + self.y_test) for elem in
                                  sublist])) + 1  # add 1 because of zero padding

        # assign a unique integer to each word/label
        self.w2idx = LabelingData.encode(self.X_train + self.X_test)
        self.l2idx = LabelingData.encode(self.y_train + self.y_test)

        # encode() maps each word to a unique index, starting from 1. We additionally incerement all the
        # values by 1, so that we can save space for 0 and 1 to be assigned to <PAD> and <UNK> later
        self.w2idx = Counter(self.w2idx)
        self.w2idx.update(self.w2idx.keys())
        self.w2idx = dict(
            self.w2idx)  # convert back to regular dict (to avoid erroneously assigning 0 to unknown words)

        self.w2idx['<PAD>'] = 0
        self.w2idx['<UNK>'] = 1

        # on the label side we only have the <PADLABEL> to add
        self.l2idx['<PADLABEL>'] = 0

        # keep the reverse to be able to decode back
        self.idx2w = {v: k for k, v in self.w2idx.items()}
        self.idx2l = {v: k for k, v in self.l2idx.items()}

        X_train_enc = [[self.w2idx[w] for w in sent] for sent in self.X_train]
        X_test_enc = [[self.w2idx[w] for w in sent] for sent in self.X_test]

        y_train_enc = [[self.l2idx[l] for l in labels] for labels in self.y_train]
        y_test_enc = [[self.l2idx[l] for l in labels] for labels in self.y_test]

        # zero-pad all the sequences
        self.max_length = len(max(self.X_train + self.X_test, key=len))

        self.X_train_enc = pad_sequences(X_train_enc, maxlen=self.max_length, padding='post')
        self.X_test_enc = pad_sequences(X_test_enc, maxlen=self.max_length, padding='post')

        y_train_enc = pad_sequences(y_train_enc, maxlen=self.max_length, padding='post')
        y_test_enc = pad_sequences(y_test_enc, maxlen=self.max_length, padding='post')

        # one-hot encode the labels
        idx = np.array(list(self.idx2l.keys()))
        vec = to_categorical(idx)
        one_hot = dict(zip(idx, vec))
        self.inv_one_hot = {tuple(v): k for k, v in one_hot.items()}  # keep the inverse dict

        self.y_train_enc = np.array([[one_hot[l] for l in labels] for labels in y_train_enc])
        self.y_test_enc = np.array([[one_hot[l] for l in labels] for labels in y_test_enc])

        print('Training y encoded shape is ', y_train_enc.shape)
        print('Maximum sequence length is', self.max_length)

    def get_embedding_layer(self, embedding_file, embedding_dim, trainable=False):
        wvmodel = KeyedVectors.load_word2vec_format(embedding_file)

        embedding_dimension = embedding_dim
        embedding_matrix = np.zeros((self.vocab_size, embedding_dimension))

        UNKOWN = np.random.uniform(-1, 1, embedding_dimension)  # assumes that '<UNK>' does not exist in the embed vocab

        for word, i in self.w2idx.items():
            if word in wvmodel.vocab:
                embedding_matrix[i] = wvmodel[word]
            else:
                embedding_matrix[i] = UNKOWN

        embedding_matrix[self.w2idx['<PAD>']] = np.zeros((embedding_dimension))

        embedding_layer = Embedding(embedding_matrix.shape[0],
                                    embedding_matrix.shape[1],
                                    weights=[embedding_matrix],
                                    trainable=trainable,
                                    name='embed_layer')
        return embedding_layer


    @staticmethod
    def tolower(file):
        lines=[l.lower() for l in FileUtility.load_list(file)]
        FileUtility.save_list(file+'new',lines)


    @staticmethod
    def labeling_file_reader(file):
        with open(file, 'r') as f:
            train = f.read().splitlines()
            X, y = [], []
            sent = []
            sent_labels = []
        for elem in train:
            if elem == '':
                X.append(sent)
                y.append(sent_labels)
                sent = []
                sent_labels = []
            else:
                xx, yy = elem.split()
                sent.append(xx)
                sent_labels.append(yy)

        lengths = LabelingData.sequence_lengths(file)
        sorted_idxs = argsort(lengths)
        lengths.sort()
        X = [X[i] for i in sorted_idxs]
        y = [y[i] for i in sorted_idxs]
        return X, y, lengths

    @staticmethod
    def convert_to_kmer(input_file, out_file, n=3):
        train = FileUtility.load_list(input_file)
        training_data = [line.split() for line in train]
        final_list = list()
        temp = []
        for x in training_data:
            if x == []:
                final_list.append(temp)
                temp = []
            else:
                temp.append(x)
        res = []
        for prot in final_list:
            sentence = ''.join(['$'] + [aa[0] for aa in prot] + ['#'])
            res += [(sentence[i:i + n], prot[i][1]) for i in range(len(sentence) - n + 1)]
            res += ['']
        FileUtility.save_list(out_file, [' '.join(list(x)) for x in res])

    @staticmethod
    def sequence_lengths(input_file):
        train = FileUtility.load_list(input_file)
        training_data = [line.split() for line in train]
        final_list = list()
        temp = []
        for x in training_data:
            if x == []:
                final_list.append(temp)
                temp = []
            else:
                temp.append(x)
        return [len(prot) for prot in final_list]

    @staticmethod
    def encode(sequence):
        '''
        Encoding sequence to integers
        :param sents:
        :return:
        '''
        t = Tokenizer(filters='\t\n', lower=False)
        t.fit_on_texts([" ".join(seq) for seq in sequence])
        return t.word_index

    @staticmethod
    def numpy2trainfiles(file,name,out='../data/s8_features/'):
        '''
        test_file='/mounts/data/proj/asgari/dissertation/datasets/deepbio/protein_general/ss/data/cb513+profile_split1.npy'
        train_file='/mounts/data/proj/asgari/dissertation/datasets/deepbio/protein_general/ss/data/cullpdb+profile_6133_filtered.npy'
        :param name:
        :param out:
        :return:
        '''
        db=np.load(file)
        a = np.arange(0,21)
        b = np.arange(35,56)
        c = np.hstack((a,b))
        db = np.reshape(db, (db.shape[0], int(db.shape[1] / 57), 57))
        seq=['A', 'C', 'E', 'D', 'G', 'F', 'I', 'H', 'K', 'M', 'L', 'N', 'Q', 'P', 'S', 'R', 'T', 'W', 'V', 'Y', 'X','NoSeq']
        label=['L', 'B', 'E', 'G', 'I', 'H', 'S', 'T']
        sequences=[]
        labels=[]
        possible_features=dict()
        for i in range(0,db.shape[0]):
            sequences.append(''.join([seq[np.argmax(x)] if np.max(x)==1 else '' for x in db[i,:,0:21]]).lower())
            labels.append(''.join([label[np.argmax(y)] if np.max(y)==1 else '' for y in db[i,:,22:30]]).lower())
        lengths=[len(x) for x in sequences]
        sorted_idxs = argsort(lengths)
        lengths.sort()
        sequences = [sequences[i] for i in sorted_idxs]
        labels = [labels[i] for i in sorted_idxs]
        FileUtility.save_list(out+name,['\n'.join([' '.join([elx,labels[idx][idy]]) for idy,elx in enumerate(list(seq))]+['']) for idx,seq in enumerate(sequences)])
        db_new=db[sorted_idxs,:,:]
        label_encoding=[[([0] if np.max(row)==1 else [1])+row for row in db_new[i,:,22:30].tolist()] for i in range(0,db.shape[0])]
        np.save(out+name+'_mat_Y',label_encoding)
        db_new =db_new[:,:,c]
        np.save(out+name+'_mat_X',db_new)
        FileUtility.save_list(out+name+'_length.txt',[str(l) for l in lengths])

    @staticmethod
    def X2extended(X):
        EMB=np.load('/mounts/data/proj/asgari/dissertation/git_repos/DeepSeq2Sec/pretrained_embeddings/emb2features.npy')
        x_new=[]
        for i in range(0,X.shape[0]):
            temp=[]
            for j in range(0,700):
                temp.append(X[i,j,0:21].dot(EMB).tolist()+X[i,j,:].tolist())
            x_new.append(temp)
        return np.array(X_new)


if __name__ == '__main__':
    LabelingData.tolower('/mounts/data/proj/asgari/dissertation/git_repos/DeepSeq2Sec/data/epitopes/test_epitopes.txt')
    LabelingData.tolower('/mounts/data/proj/asgari/dissertation/git_repos/DeepSeq2Sec/data/epitopes/train_epitopes.txt')
