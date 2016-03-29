import pandas as pd
import pickle

SLURM_OUT = "../slurm_out"
from subprocess import Popen
import time

out_overall = pickle.load(open('../data/input/all_regions.pkl','r'))

train_region = "SanDiego"
test_region = "Austin"

train_df = out_overall[train_region]
test_df = out_overall[test_region]
K=3
for K in [1, 2, 4, 5]:

    for transform in ["DD",'None']:
        print transform
        print "*"*40
        count = 0
        for test_home in test_df.index:
            count+= 1
            print test_home, count, len(test_df.index)
            #for appliance in ["hvac","fridge","dr","wm"]:
            for appliance in ["hvac"]:
                for month in range(1, 13):
                    OFILE = "%s/%s_%s_%d_%s_%d_%s.out" % (SLURM_OUT, train_region, test_region, test_home, appliance, month, transform )
                    EFILE = "%s/%s_%s_%d_%s_%d_%s.err" % (SLURM_OUT, train_region, test_region, test_home, appliance, month, transform )

                    SLURM_SCRIPT = "%s_%s_%d_%s_%d_%s.pbs" % (train_region, test_region, test_home, appliance, month, transform)
                    CMD = 'python ../new_experiments/create_inequalities.py %s %s %d %s %d %s %d' % (train_region, test_region,
                                                                                                     test_home, appliance, month,
                                                                                                     transform, K)
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
                    Popen(command)
            print "Now sleeping.."
            time.sleep(0.25)
        time.sleep(30)

