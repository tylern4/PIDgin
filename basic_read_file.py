# Use these if running on a ssh session
# import matplotlib
# matplotlib.use('agg')

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys
from pymongo import MongoClient


def main(infile, time='10s'):
    # Loads in the data and sets the first column as the index
    # And parses the column as dates for easier plotting
    total_data = pd.read_csv(infile, index_col=[0], parse_dates=[0])
    total_out = []
    processes = total_data.pid.unique()
    for proc in processes:
        output_data = pd.DataFrame()
        # select out for each process
        data = total_data[total_data.pid == proc]
        # Get a rolling difference over a 10s window
        # We can tune this before saving data to a DB
        output_data['cpu_usage'] = (data['cpu_t_system'] + data['cpu_t_user']
                                    ).rolling(time).apply(lambda x: x.iloc[-1] - x.iloc[0])

        # Can also multiply by 1e-9 to get GB
        # Look into difference of mean/mac for these values
        output_data['mem_usage'] = (data['mem_rss'] + data['mem_vms']
                                    ).rolling(time).max()

        # Reads and writes also need to get differences
        # Will probabaly also need to get units correct
        for read_write in ['read', 'write']:
            for count_chars in ['count', 'chars']:
                output_data[f'{read_write}_{count_chars}_diff'] = data[f'{read_write}_{count_chars}'].rolling(
                    "10s").apply(lambda x: x.iloc[-1] - x.iloc[0])

        # Other columns can be copied over
        for copy_col in ['pid', 'name', 'num_threads', 'num_fds', 'cmdline']:
            output_data[copy_col] = data[copy_col]
        total_out.append(output_data)

    # Can either send them as different dataframes
    # for df in total_out:
    #   upload to db

    # Or concat and return as a single to be parsed again later
    # total = pd.concat(total_out)

    return total_out


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
    fig, ax = plt.subplots()

    for p in out:
        # p.cpu_usage.plot(ax=ax, label=f'{p.name.unique()}')
        p.mem_usage.plot(ax=ax, label=f'{p.name.unique()}')
        # plt.title(f'{p.name.iloc[0]}, {p.cmdline.iloc[0]}, {p.pid.iloc[0]}')

    plt.legend()
    plt.show()
    # client = MongoClient('mongodb://%s:%s@127.0.0.1:%s' %
    #                      ('root', '123456', '7017'))

    # db = client['jaws_db']
    # col = db['performance']

    # for df in out:
    #     name = df.name.iloc[0]
    #     df.index = df.index.astype(str)
    #     col.insert_one({name: df.T.to_dict()})
