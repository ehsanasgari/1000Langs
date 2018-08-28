import sys
from utility.file_utility import FileUtility
from nltk import FreqDist
import tqdm

files=FileUtility.recursive_glob('/mounts/data/proj/asgari/superparallelproj/paralleltext/bibles/corpus/','*.txt')
urls=[]
for f in tqdm.tqdm(files):
    urls+=['\t'.join([l,f.split('/')[-1][0:3],f.split('/')[-1]]) for l in  FileUtility.load_list(f)[0:30] if 'url' in l.lower()]

urls.sort()

FileUtility.save_list('config/url.txt',urls)
