SLURM_OUT = "../../slurm_out"
from subprocess import Popen
import time
from matrix_factorisation import nmf_features, transform, transform_2, preprocess, get_static_features
import  os

import numpy as np
import pandas as pd
import pickle
import sys
from subprocess import Popen
sys.path.append("../../code")
from features import feature_map
import subprocess

def _save_results(appliance, lat, feature_comb, test_home, pred_df):
    pred_df.to_csv(os.path.expanduser("~/collab/%s_%d_%s_%d.csv" %(appliance, lat, '_'.join(feature_comb), test_home)))

out_overall = pickle.load(open('../../data/input/all_regions.pkl', 'r'))

region = "Austin"

df = out_overall[region]

df_copy = df.copy()
#drop_rows_having_no_data
o = {}
for h in df.index:
    o[h]=len(df.ix[h][feature_map['Monthly+Static']].dropna())
num_features_ser = pd.Series(o)
drop_rows = num_features_ser[num_features_ser==0].index

df = df.drop(drop_rows)
dfc = df.copy()


df = df.rename(columns={'house_num_rooms':'num_rooms',
                        'num_occupants':'total_occupants',
                        'difference_ratio_min_max':'ratio_difference_min_max'})




from all_functions import *
from features_larger import *

import itertools
feature_combinations = [['None']]
for l in range(1,4):
    for a in itertools.combinations(['occ','area','rooms'], l):
        feature_combinations.append(list(a))

import time

for appliance in ['hvac','fridge','dw','wm','mw','oven']:

    if appliance=="hvac":
        start, end = 5,11
    else:
        start, end=1,13
    X_matrix, X_normalised, col_max, col_min, appliance_cols, aggregate_cols = preprocess(df, dfc, appliance)
    static_features= get_static_features(dfc, X_normalised)
    from copy import deepcopy
    all_cols = deepcopy(appliance_cols)
    all_cols.extend(aggregate_cols)

    for home in X_matrix.index:
        OFILE = "%s/%s_%d.out" % (SLURM_OUT, appliance, home)
        EFILE = "%s/%s_%d.err" % (SLURM_OUT, appliance, home)
        SLURM_SCRIPT = "%s_%d.pbs" %(appliance, home)
        CMD = 'python train_all_homes_test_all_homes.py %s %d' %(appliance, home)
        lines = []
        lines.append("#!/bin/sh\n")
        lines.append('#SBATCH --time=0-01:0:00\n')
        lines.append('#SBATCH --mem=16\n')
        lines.append('#SBATCH -o '+'"' +OFILE+'"\n')
        lines.append('#SBATCH -e '+'"' +EFILE+'"\n')
        lines.append(CMD+'\n')

        with open(SLURM_SCRIPT, 'w') as f:
           f.writelines(lines)
        command = ['sbatch', SLURM_SCRIPT]
        time.sleep(10)
        print Popen(command)
    print "Now sleeping.."
