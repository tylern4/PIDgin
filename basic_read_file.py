# Use these if running on a ssh session
# import matplotlib
# matplotlib.use('agg')

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys
from pymongo import MongoClient
import json
import logging


def process_pid(data, time='10s'):
    output_data = {}
    # Basic runtime stats
    output_data['start_time'] = str(
        data.index[0].strftime("%m-%d-%Y %H:%M:%S.%f"))
    output_data['end_time'] = str(
        data.index[-1].strftime("%m-%d-%Y %H:%M:%S.%f"))
    output_data['runtime_sec'] = float(
        (data.index[-1] - data.index[0]).total_seconds())

    # Copy over metadata once
    for copy_col in ['name', 'cmdline']:
        output_data[copy_col] = str(data[copy_col].iloc[0])

    # Get a rolling difference over a window
    # We can tune this before saving data to a DB
    cpu_usage = (data['cpu_time_system'] + data['cpu_time_user']
                 ).rolling(time).apply(lambda x: x.iloc[-1] - x.iloc[0])
    cpu_usage = cpu_usage.resample(time).mean()
    iowait_usage = data['iowait'].rolling(
        time).apply(lambda x: x.iloc[-1] - x.iloc[0])
    iowait_usage = iowait_usage.resample(time).mean()
    mem_usage = (data['mem_rss'] + data['mem_vms']).rolling(time).max()
    mem_usage = mem_usage.resample(time).mean()

    output_data['timeseries'] = list(
        cpu_usage.index.to_series().dt.strftime("%m-%d-%Y %H:%M:%S.%f"))
    output_data['cpu_usage'] = list(cpu_usage)
    output_data['iowait_usage'] = list(iowait_usage)
    output_data['mem_usage'] = list(mem_usage)

    # Reads and writes also need to get differences
    # Will probabaly also need to get units correct
    for read_write in ['read', 'write']:
        for count_chars in ['count', 'chars']:
            output_data[f'{read_write}_{count_chars}_diff'] = list(data[f'{read_write}_{count_chars}'].rolling(
                time).apply(lambda x: x.iloc[-1] - x.iloc[0]))

    # Other columns can be copied over
    for copy_col in ['num_threads', 'num_fds']:
        output_data[copy_col] = list(data[copy_col])

    try:
        return output_data
    except Exception as e:
        logging.debug(e)


def main(infile, time='10s'):
    # Loads in the data and sets the first column as the index
    # And parses the column as dates for easier plotting
    total_data = pd.read_csv(infile, index_col=[0], parse_dates=[0])
    print(total_data.head())
    total = total_data.groupby(['pid']).apply(process_pid, time)

    for process in total.items():
        print(process.keys())
        # df.index = df.index.astype(str)
        # col.insert_one({name: df.T.to_dict()})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str,
                        help="Input file csv from pagurus",
                        default=None)

    args = parser.parse_args()
    if args.input == None:
        parser.print_help()
        exit()

    out = main(infile=args.input)
    # fig, ax = plt.subplots()

    # for p in out:
    #     # p.cpu_usage.plot(ax=ax, label=f'{p.name.unique()}')
    #     p.mem_usage.plot(ax=ax, label=f'{p.name.unique()}')
    #     # plt.title(f'{p.name.iloc[0]}, {p.cmdline.iloc[0]}, {p.pid.iloc[0]}')

    # plt.legend()
    # plt.show()
    # client = MongoClient('mongodb://%s:%s@127.0.0.1:%s' %
    #                      ('root', '123456', '7017'))

    # db = client['jaws_db']
    # col = db['performance']
