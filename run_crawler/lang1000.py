import sys

sys.path.append('../')
from utility.visualization_utility import methods2venn2
import pandas as pd
import numpy as np
from metaAPI.metadata import getMassiveparallel_meta
from bdpAPI.bdpAPI import BDPAPl
from bibleCLOUDAPI.biblecloudAPI import BibleCloudAPl
from biblePNGAPI.pngAPI import PNGAPl
from bibleCOMAPI.biblecomAPI import BibleComAPl
import argparse
import warnings
import requests

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def checkArgs(args):
    '''
        This function checks the input arguments and returns the extracted inputs and if there is an error False
    '''
    # Using the argument parser in case of -h or wrong usage the correct argument usage
    # will be prompted
    parser = argparse.ArgumentParser()
    #5120f8eb40005070f19e9
    # output directory #################################################################################################
    parser.add_argument('--outdir', action='store', dest='output_dir', default=False, type=str,
                        help="directory for storing the output files, if doesn't exist will be created.")
    #f03a423aad9
    # output directory #################################################################################################
    parser.add_argument('--apikey', action='store', dest='apikey', default=False, type=str,
                        help="API key of the Bible Digital Platform")

    # to override the previous files or to continue ####################################################################
    parser.add_argument('--override', action='store', dest='override', default=1, type=int,
                        help='Override the existing files?')

    # to override the previous files or to continue ####################################################################
    parser.add_argument('--repeat', action='store', dest='repeat', default=4, type=int,
                        help='Maximum trials on a source to retrieve more languages?')

    # to override the previous files or to continue ####################################################################
    parser.add_argument('--updatemeta', action='store', dest='updatemeta', default=1, type=int,
                        help='Would you like to update metadata information from the sources? 1 otherwise 0')

    # cores ################################################################################################
    parser.add_argument('--cores', action='store', dest='cores', default=4, type=int,
                        help='Number of cores to be used, default is 4')

    try:
        parsedArgs = parser.parse_args()

        response = requests.get('https://dbt.io/api/apiversion?key=' + parsedArgs.apikey + '&v=2')
        if response.status_code != 200:
            print('Enter a correct API code')
            return False
        else:
            print('The API code is verified..')
        return parsedArgs.output_dir, parsedArgs.override, parsedArgs.updatemeta, parsedArgs.apikey, parsedArgs.cores, parsedArgs.repeat
    except:
        exit(0)
        return False


if __name__ == '__main__':

    warnings.filterwarnings('ignore')
    out = checkArgs(sys.argv)
    if not out:
        exit()
    else:
        output_dir, override, updatemeta, apikey, cores, repeat = out

        # parameters
        out_path = output_dir
        nump = cores
        update_metadata = (override == 1)
        override = (updatemeta == 1)

        print('=====================================')
        print('>>>> The PBC files are being generated at '+out_path )
        print('=====================================')


        # print('=====================================')
        # print('>>>> Start retrieveing parallel bibles from the bible digital platform..')
        # print('=====================================')
        # # API call
        # BDP_obj = BDPAPl(apikey, out_path)
        # BDP_obj.create_BPC(nump=nump, update_meta_data=update_metadata, override=override, repeat=repeat)
        #
        # print('=====================================')
        # print('<<<< ✓ Retrieveing parallel bibles from bible digital platform is completed..')
        # print(' Report is generated at '+out_path+'/reports/'+'crawl_report_API.tsv')
        # print(' Aggregated report '+out_path+'/reports/'+'final_rep.tsv')
        # print('=====================================')
        # print("")
        # print("")
        #
        #
        # print('=====================================')
        # print('>>>> Start retrieveing parallel bibles from biblecloud..')
        # print('=====================================')
        # # BibleCloud call
        # CL = BibleCloudAPl(out_path)
        # CL.crawl_bible_cloud(nump=nump, override=override, repeat=repeat)
        # print('=====================================')
        # print('<<<< ✓ Retrieveing parallel bibles from bible cloud is completed..')
        # print(' Report is generated at '+out_path+'/reports/'+'crawl_report_cloud.tsv')
        # print(' Aggregated report '+out_path+'/reports/'+'final_rep.tsv')
        # print('=====================================')
        # print("")
        # print("")
        #
        # print('=====================================')
        # print('>>>> Start retrieveing parallel bibles from PNGscripture..')
        # print('=====================================')
        # # PNG call
        # PNG = PNGAPl(out_path)
        # PNG.crawl_bpc(nump=nump, override=override, repeat=repeat)
        # print('=====================================')
        # print('<<<< ✓ Retrieveing parallel bibles from PNGscripture is completed..')
        # print(' Report is generated at '+out_path+'/reports/'+'crawl_report_png.tsv')
        # print(' Aggregated report '+out_path+'/reports/'+'final_rep.tsv')
        # print('=====================================')
        # print("")
        # print("")


        print('=====================================')
        print('>>>> Start retrieveing parallel bibles from biblecom..')
        print('=====================================')
        # BibleCom
        BCA = BibleComAPl(out_path)
        BCA.crawl_bpc(nump=nump, update_meta=update_metadata, override=override, repeat=repeat)
        print('=====================================')
        print('<<<< ✓ Retrieveing parallel bibles from biblecom is completed..')
        print(' Report is generated at '+out_path+'/reports/'+'crawl_report_biblecom.tsv')
        print(' Aggregated report '+out_path+'/reports/'+'final_rep.tsv')
        print('=====================================')
        print("")
        print("")


        print('>>>> Comparison with massively parallel bible corpora ')
        df_massivepar = getMassiveparallel_meta(update=False)

        out_path = out_path
        df_1000Langs = pd.read_table(out_path + '/reports/final_rep.tsv')
        df_1000Langs_stat = dict()
        for x, y in df_1000Langs.groupby('language_iso')['verses'].apply(list).to_dict().items():
            df_1000Langs_stat[x] = [len(y), max(y), np.mean(y)]

        rows = []
        for iso, scores in df_1000Langs_stat.items():
            rows.append([iso, scores[0], scores[1], scores[2]])
        df_1000Langs = pd.DataFrame(rows)
        df_1000Langs = df_1000Langs.rename(index=str,
                                           columns={0: 'language_iso', 1: '#trans-1000Langs', 2: 'max-verse-1000Langs',
                                                    3: 'mean-verse-1000Langs'})
        df_1000Langs = df_1000Langs.set_index('language_iso')

        lange_overlap = {'MassiveParallel': df_massivepar.language_iso.tolist(),
                         '1000Langs': df_1000Langs.index.tolist()}

        l = methods2venn2(lange_overlap, name=out_path + '/reports/venn')

        comp_table = df_1000Langs.join(df_massivepar.set_index('language_iso'), on='language_iso')
        comp_table = comp_table.fillna(0)
        writer = pd.ExcelWriter(out_path+'/reports/comparison.xlsx')
        comp_table.to_excel(writer, 'Comparison with massively parallel corpora')
        writer.save()
        print('In ', comp_table[comp_table['max-verse-1000Langs'] >= comp_table['max-verse-massivepar']].shape[0],
              ' iso codes out of ', comp_table.shape[0],
              ' total, 1000Langs crawled more verses for that language!')
        print('In ', comp_table[(comp_table['max-verse-1000Langs'] >= comp_table['max-verse-massivepar']) & (
                    comp_table['max-verse-massivepar'] > 0)].shape[0], ' iso codes out of ',
              comp_table[(comp_table['max-verse-1000Langs'] > 0) & (comp_table['max-verse-massivepar'] > 0)].shape[0],
              ' total intersections, 1000Langs crawled more verses in that language!')


        print('>>>> Comparison with massively parallel bible corpora ')
        print(' See the Venn diagram '+out_path+'/reports/'+'venn.pdf')
        print(' See the detailed report on the comparison of the crawled corpus with the massively parallel corpus here: '+out_path+'/reports/comparison.xlsx')
