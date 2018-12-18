__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__website__ = "https://llp.berkeley.edu/asgari/"
__git__ = "https://github.com/ehsanasgari/"
__email__ = "ehsan.asgari@gmail.com"
__project__ = "1000Langs -- Super parallel project at CIS LMU"


import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import sys
sys.path.append('../')
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from utility.file_utility import FileUtility
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import *

global color_schemes
color_schemes=[['green','blue','red','gold', 'cyan'], ['#ff0505', '#f2a041', '#cdff05', '#04d9cb', '#45a8ff', '#8503a6', '#590202', '#734d02', '#4ab304', '#025359', '#0454cc', '#ff45da', '#993829', '#ffda45', '#1c661c', '#05cdff', '#1c2f66', '#731f57', '#b24a04', '#778003', '#0e3322', '#024566', '#0404d9', '#e5057d', '#66391c', '#31330e', '#3ee697', '#2d7da6', '#20024d', '#33011c']+list(({'aliceblue':            '#F0F8FF','antiquewhite':         '#FAEBD7','aqua':                 '#00FFFF','aquamarine':           '#7FFFD4','azure':                '#F0FFFF','beige':                '#F5F5DC','bisque':               '#FFE4C4','black':                '#000000','blanchedalmond':       '#FFEBCD','blue':                 '#0000FF','blueviolet':           '#8A2BE2','brown':                '#A52A2A','burlywood':            '#DEB887','cadetblue':            '#5F9EA0','chartreuse':           '#7FFF00','chocolate':            '#D2691E','coral':                '#FF7F50','cornflowerblue':       '#6495ED','cornsilk':             '#FFF8DC','crimson':              '#DC143C','cyan':                 '#00FFFF','darkblue':             '#00008B','darkcyan':             '#008B8B','darkgoldenrod':        '#B8860B','darkgray':             '#A9A9A9','darkgreen':            '#006400','darkkhaki':            '#BDB76B','darkmagenta':          '#8B008B','darkolivegreen':       '#556B2F','darkorange':           '#FF8C00','darkorchid':           '#9932CC','darkred':              '#8B0000','darksalmon':           '#E9967A','darkseagreen':         '#8FBC8F','darkslateblue':        '#483D8B','darkslategray':        '#2F4F4F','darkturquoise':        '#00CED1','darkviolet':           '#9400D3','deeppink':             '#FF1493','deepskyblue':          '#00BFFF','dimgray':              '#696969','dodgerblue':           '#1E90FF','firebrick':            '#B22222','floralwhite':          '#FFFAF0','forestgreen':          '#228B22','fuchsia':              '#FF00FF','gainsboro':            '#DCDCDC','ghostwhite':           '#F8F8FF','gold':                 '#FFD700','goldenrod':            '#DAA520','gray':                 '#808080','green':                '#008000','greenyellow':          '#ADFF2F','honeydew':             '#F0FFF0','hotpink':              '#FF69B4','indianred':            '#CD5C5C','indigo':               '#4B0082','ivory':                '#FFFFF0','khaki':                '#F0E68C','lavender':             '#E6E6FA','lavenderblush':        '#FFF0F5','lawngreen':            '#7CFC00','lemonchiffon':         '#FFFACD','lightblue':            '#ADD8E6','lightcoral':           '#F08080','lightcyan':            '#E0FFFF','lightgoldenrodyellow': '#FAFAD2','lightgreen':           '#90EE90','lightgray':            '#D3D3D3','lightpink':            '#FFB6C1','lightsalmon':          '#FFA07A','lightseagreen':        '#20B2AA','lightskyblue':         '#87CEFA','lightslategray':       '#778899','lightsteelblue':       '#B0C4DE','lightyellow':          '#FFFFE0','lime':                 '#00FF00','limegreen':            '#32CD32','linen':                '#FAF0E6','magenta':              '#FF00FF','maroon':               '#800000','mediumaquamarine':     '#66CDAA','mediumblue':           '#0000CD','mediumorchid':         '#BA55D3','mediumpurple':         '#9370DB','mediumseagreen':       '#3CB371','mediumslateblue':      '#7B68EE','mediumspringgreen':    '#00FA9A','mediumturquoise':      '#48D1CC','mediumvioletred':      '#C71585','midnightblue':         '#191970','mintcream':            '#F5FFFA','mistyrose':            '#FFE4E1','moccasin':             '#FFE4B5','navajowhite':          '#FFDEAD','navy':                 '#000080','oldlace':              '#FDF5E6','olive':                '#808000','olivedrab':            '#6B8E23','orange':               '#FFA500','orangered':            '#FF4500','orchid':               '#DA70D6','palegoldenrod':        '#EEE8AA','palegreen':            '#98FB98','paleturquoise':        '#AFEEEE','palevioletred':        '#DB7093','papayawhip':           '#FFEFD5','peachpuff':            '#FFDAB9','peru':                 '#CD853F','pink':                 '#FFC0CB','plum':                 '#DDA0DD','powderblue':           '#B0E0E6','purple':               '#800080','red':                  '#FF0000','rosybrown':            '#BC8F8F','royalblue':            '#4169E1','saddlebrown':          '#8B4513','salmon':               '#FA8072','sandybrown':           '#FAA460','seagreen':             '#2E8B57','seashell':             '#FFF5EE','sienna':               '#A0522D','silver':               '#C0C0C0','skyblue':              '#87CEEB','slateblue':            '#6A5ACD','slategray':            '#708090','snow':                 '#FFFAFA','springgreen':          '#00FF7F','steelblue':            '#4682B4','tan':                  '#D2B48C','teal':                 '#008080','thistle':              '#D8BFD8','tomato':               '#FF6347','turquoise':            '#40E0D0','violet':               '#EE82EE','wheat':                '#F5DEB3','white':                '#FFFFFF','whitesmoke':           '#F5F5F5','yellow':               '#FFFF00','yellowgreen':          '#9ACD32'}).keys()),['#ff0505', '#f2a041', '#cdff05', '#04d9cb', '#45a8ff', '#8503a6', '#590202', '#734d02', '#4ab304', '#025359', '#0454cc', '#ff45da', '#993829', '#ffda45', '#1c661c', '#05cdff', '#1c2f66', '#731f57', '#b24a04', '#778003', '#0e3322', '#024566', '#0404d9', '#e5057d', '#66391c', '#31330e', '#3ee697', '#2d7da6', '#20024d', '#33011c']]


from matplotlib import pyplot as plt
from matplotlib_venn import venn2,venn3, venn3_circles
import matplotlib
import matplotlib.pyplot as plt

import itertools
import operator

def generate_binary(N):
    return [''.join(list(b)[::-1]) for b in  ['{:0{}b}'.format(i, N) for i in range(2**N)][1::]]
def get_intersection_of_list(list_of_list_features):
    return list(set.intersection(*map(set, list_of_list_features)))

def get_max_of_dict(inp):
    return max(inp.items(), key=operator.itemgetter(1))[0]

def methods2venn(res_dict, name=None):
    '''
        Plot the overlap of sets in the dictionary
        return: accumulative of all intersections > 1
    '''
    all_methods=list(res_dict.keys())
    all_methods.sort()
    figure(figsize=(20,50))
    threesets=list(itertools.combinations(all_methods,3))
    final_list=[]
    for idx,methods in enumerate(threesets):
        if idx<10:
            methods=list(methods)
            methods.sort()
            binary_sets=generate_binary(len(methods))
            subsets_sizes=tuple([len(get_intersection_of_list([list(res_dict[methods[idx]])  for idx,x in enumerate(list(setting))  if x=='1' ])) for setting in binary_sets])
            at_least_intersection=[x for x in binary_sets if x.count('1')>1]
            final_list+=list(itertools.chain(*[get_intersection_of_list([list(res_dict[methods[idx]])  for idx,x in enumerate(list(setting))  if x=='1' ]) for setting in at_least_intersection]))
            subplot(5,2,idx+1)
            v = venn3(subsets=subsets_sizes, set_labels=tuple(methods))
    plt.tight_layout()
    #plt.show()
    if name:
        plt.savefig(name)
    return final_list

def methods2venn2(res_dict, name=None):
    '''
        Plot the overlap of sets in the dictionary
        return: accumulative of all intersections > 1
    '''
    methods=list(res_dict.keys())
    methods.sort()
    figure(figsize=(10,10))
    final_list=[]
    binary_sets=generate_binary(len(methods))
    subsets_sizes=tuple([len(get_intersection_of_list([list(res_dict[methods[idx]])  for idx,x in enumerate(list(setting))  if x=='1' ])) for setting in binary_sets])
    at_least_intersection=[x for x in binary_sets if x.count('1')>1]
    final_list+=list(itertools.chain(*[get_intersection_of_list([list(res_dict[methods[idx]])  for idx,x in enumerate(list(setting))  if x=='1' ]) for setting in at_least_intersection]))
    v = venn2(subsets=subsets_sizes, set_labels=tuple(methods))
    plt.tight_layout()
    #plt.show()
    if name:
        plt.savefig(name+'.pdf', dpi=500)
    return final_list

def create_mat_plot(mat, axis_names, title, filename, xlab, ylab, cmap='inferno', filetype='pdf', rx=0, ry=0, font_s=10, annot=True):
    '''
    :param mat: divergence matrix
    :param axis_names: axis_names
    :param title
    :param filename: where to be saved
    :return:
    '''
    plt.rc('text', usetex=True)
    if len(axis_names)==0:
        ax = sns.heatmap(mat,annot=annot, cmap=cmap,fmt="d")
    else:
        # removed fmt="d",
        ax = sns.heatmap(mat,annot=annot, yticklabels=axis_names, xticklabels=axis_names, cmap=cmap)
    plt.title(title)
    params = {
        'legend.fontsize': font_s,
        'xtick.labelsize': font_s,
        'ytick.labelsize': font_s,
        'text.usetex': True,
    }
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    matplotlib.rcParams['mathtext.fontset'] = 'custom'
    matplotlib.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
    matplotlib.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
    matplotlib.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.xticks(rotation=rx)
    plt.yticks(rotation=ry)
    plt.rcParams.update(params)
    plt.tight_layout()
    plt.savefig(filename + '.'+filetype)
    plt.show()
    plt.clf()

def plot_scatter(ax, X, Y, x_label, y_label, title,legend_hide=True, legend_loc=4, label_dict=False, legend_size=7, legend_col=1, color_schemes_idx=1):
    plt.rc('text', usetex=True)
    global color_schemes

    target=list(set(Y))
    target.sort()
    color_idx=[target.index(x) for x in Y]
    color_list=color_schemes[color_schemes_idx]

    for current_color in range(len(target)):
        color=color_list
        current_idxs=[idx for idx,v in enumerate(color_idx) if v==current_color]
        if label_dict:
            ax.scatter(X[current_idxs, 0], X[current_idxs, 1], c=color[current_color], label=label_dict[target[current_color]], cmap='viridis', alpha=0.4, edgecolors=None)
        else:
            ax.scatter(X[current_idxs, 0], X[current_idxs, 1], c=color[current_color], label=target[current_color], cmap='viridis', alpha=0.4, edgecolors=None)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks([])
    plt.yticks([])
    ax.set_title(title)
    if not legend_hide:
        ax.legend(loc=legend_loc, bbox_to_anchor=(0.5, -0.1), prop={'size': legend_size},ncol=legend_col, edgecolor='black', facecolor='white', frameon=True)
    matplotlib.rcParams['mathtext.fontset'] = 'stix'
    matplotlib.rcParams['font.family'] = 'STIXGeneral'
    matplotlib.rcParams['mathtext.fontset'] = 'custom'
    matplotlib.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
    matplotlib.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
    matplotlib.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'
    matplotlib.rcParams["axes.edgecolor"] = "black"
    matplotlib.rcParams["axes.linewidth"] = 0.6
    rect = ax.patch
    rect.set_facecolor('white')



def plot_pca_tsne_nn(X_pca, X_tsne, X_tsne_NN, Y, filename=False,  legend_size=7, label_dic=False, color_idx=2, loc=[(4,1),(4,1),(4,1)]):
    plt.plot([1,2,3])
    myplot=figure(figsize=(12, 12))
    ax=subplot(221)
    plot_scatter(ax, X_pca, Y, 'PCA_1', 'PCA_0', '(i) PCA over 6-mer representations',legend_hide=True, legend_loc=loc[0][0], legend_col=loc[0][1], legend_size=legend_size, label_dict=label_dic, color_schemes_idx=color_idx)
    ax=subplot(222)
    plot_scatter(ax, X_tsne, Y, 't-SNE_1', 't-SNE_0', '(ii) t-SNE over 6-mer representations',legend_hide=False,  legend_loc=9, legend_col=loc[1][1],  legend_size=legend_size,label_dict=label_dic, color_schemes_idx=color_idx)
    ax=subplot(223)
    plot_scatter(ax, X_tsne_NN, Y, 't-SNE_1', 't-SNE_0', '(iii) t-SNE / activation function of the last layer of neural network',legend_hide=True,  legend_loc=loc[2][0], legend_col=loc[2][1],  legend_size=legend_size, label_dict=label_dic, color_schemes_idx=color_idx)
    myplot.tight_layout()
    if filename:
        plt.savefig(filename+'.pdf')
    else:
        plt.show()

def get_pca_tsne(X, X_NN):
    X_pca = PCA(n_components=50).fit_transform(X.toarray())
    X_tsne = TSNE(n_components=2, perplexity=40, verbose=2, learning_rate=10).fit_transform(X.toarray())
    X_tsne_NN = TSNE(n_components=2, perplexity=40, verbose=2, learning_rate=10).fit_transform(X_NN)
    return X_pca, X_tsne, X_tsne_NN

def create_tsne_web(X, Y, tsne_file_coor, tsne_file_label):
    classes=list(set(Y))
    classes.sort()
    L=[classes.index(y) for y in Y]
    tsne_res = np.hstack((X, np.array([L]).T))
    tsne_res[:,0:2]=np.round(tsne_res[:,0:2],2)
    tsne_lines=[]
    for l in tsne_res:
        tsne_lines.append('\t'.join([str(l[0]), str(l[1]), str(int(l[2]))]))
    FileUtility.save_list(tsne_file_coor,tsne_lines)
    FileUtility.save_list(tsne_file_label,Y)

