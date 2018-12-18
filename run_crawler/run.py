import sys
sys.path.append('../')
from utility.file_utility import FileUtility
from utility.visualization_utility import methods2venn2
import tqdm
import pandas as pd
import numpy as np
from metaAPI.metadata import getMetaMerged, getMassiveparallel_meta
from bdpAPI.bdpAPI import BDPAPl
from bibleCLOUDAPI.biblecloudAPI import BibleCloudAPl
from biblePNGAPI.pngAPI import PNGAPl
from bibleCOMAPI.biblecomAPI import BibleComAPl


if __name__ == '__main__':

    # parameters
    out_path='/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API_repeat/'
    nump=20
    update_metadata=True
    override=True
    repeat=4

    # API call
    BDP_obj = BDPAPl('f03a423aad95120f8eb40005070f19e9', out_path)
    BDP_obj.create_BPC(nump=nump,update_meta_data=update_metadata, override=override, repeat=repeat)

    # BibleCloud call
    CL=BibleCloudAPl(out_path)
    CL.crawl_bible_cloud(nump=nump, override=override, repeat=repeat)

    # PNG call
    PNG=PNGAPl(out_path)
    PNG.crawl_bpc(nump=nump,override=override, repeat=repeat)

    # BibleCom
    BCA=BibleComAPl(out_path)
    BCA.crawl_bpc(nump=nump,update_meta=update_metadata, override=override, repeat=repeat)


    df_massivepar=getMassiveparallel_meta(update=False)

    out_path=out_path
    df_1000Langs=pd.read_table(out_path+'/reports/final_rep.tsv')
    df_1000Langs_stat=dict()
    for x ,y in df_1000Langs.groupby('language_iso')['verses'].apply(list).to_dict().items():
        df_1000Langs_stat[x]=[len(y),max(y), np.mean(y)]

    rows=[]
    for iso, scores in df_1000Langs_stat.items():
        rows.append([iso, scores[0], scores[1], scores[2]])
    df_1000Langs=pd.DataFrame(rows)
    df_1000Langs=df_1000Langs.rename(index=str, columns={0:'language_iso',1:'#trans-1000Langs', 2:'max-verse-1000Langs',3:'mean-verse-1000Langs'})
    df_1000Langs=df_1000Langs.set_index('language_iso')

    lange_overlap={'MassiveParallel':df_massivepar.language_iso.tolist(),'1000Langs':df_1000Langs.index.tolist()}

    l=methods2venn2(lange_overlap, name=out_path+'/reports/venn.png')

    comp_table=df_1000Langs.join(df_massivepar.set_index('language_iso'), on='language_iso')
    comp_table=comp_table.fillna(0)
    writer = pd.ExcelWriter('../reports/comparison.xlsx')
    comp_table.to_excel(writer,'Comparison with massively parallel corpora')
    writer.save()
    print ('In ',comp_table[comp_table['max-verse-1000Langs']>=comp_table['max-verse-massivepar']].shape[0], ' out iso codes of ', comp_table.shape[0],' total, 1000Langs crawled larger max verses for the iso code!')
    print ('In ',comp_table[(comp_table['max-verse-1000Langs']>=comp_table['max-verse-massivepar']) & (comp_table['max-verse-massivepar']>0)].shape[0], ' out iso codes of ', comp_table[(comp_table['max-verse-1000Langs']>0) & (comp_table['max-verse-massivepar']>0)].shape[0],' total intersection, 1000Langs crawled larger max verses for the iso code!')
