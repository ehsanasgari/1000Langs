import sys
sys.path.append('../')

if __name__ == '__main__':
    BDP_obj = BDPCall('f03a423aad95120f8eb40005070f19e9',
                      '/mounts/data/proj/asgari/final_proj/000_datasets/testbib/API')
    BDP_obj.create_BPC()
