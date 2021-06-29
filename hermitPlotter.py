#!/usr/bin/env python3
import argparse
import os
import logging

try:
    import matplotlib  # noqa
    matplotlib.use('agg')  # noqa
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    import sys
    print("Error: Install pandas and matplotlib to plot!", file=sys.stderr)


def plotter(infile: str):
    """
    Plot the results from the runner step. 
    It can be done after the fact with `-j` option to just plot.

    Args:
        infile (str, optional): Input filename for csv. Defaults to "stats.csv".
    """

    tag = infile

    # Load in dataframe and put 0th column as DateTimeIndex
    df = pd.read_csv(infile,
                     index_col=[0],
                     parse_dates=[0])

    df['cpu_percent'].plot()
    df['cpu_percent'].rolling('60s').mean().plot(label="Average usage (1m)")
    df['cpu_percent'].rolling('120s').mean().plot(label="Average usage (2m)")
    plt.title(f"cpu percentage {tag}")
    plt.ylabel("cpu percentage [%]")
    plt.xlabel("time")
    lgn = plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    if tag is None:
        plt.savefig("cpu.png")
    else:
        plt.savefig(f"{tag}_cpu.png",
                    bbox_extra_artists=[lgn],
                    bbox_inches='tight')

    # Clear plot for next plot
    # Faster then making a new one
    plt.clf()

    df['mem_rss'] = df['mem_rss'] * 1e-9
    df['mem_rss'].plot(label="Raw memory usage")
    df['mem_rss'].rolling('60s').mean().plot(
        label="Average usage (1m)")
    df['mem_rss'].rolling('120s').mean().plot(
        label="Average usage (2m)")
    plt.title(f"memory usage {tag}")
    plt.ylabel("memory usage [MB]")
    plt.xlabel("time")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    if tag is None:
        plt.savefig("mem.png")
    else:
        plt.savefig(f"{tag}_mem.png",
                    bbox_extra_artists=[lgn],
                    bbox_inches='tight')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tag", type=str,
                        help="Tags the process and gives a name to the plots and statistcs csv file.", default=None)
    parser.add_argument("-o", "--outfile", type=str,
                        help="Output file name for csv.",
                        default=None)
    parser.add_argument("-I", "--infile", type=str,
                        help="Input csv for plotting. Only used with -j option.",
                        default=None)
    parser.add_argument("-np", "--no-plot", action="store_false",
                        help="Plot the data.", default=True)
    parser.add_argument("-j", "--just-plot", action="store_true",
                        help="Don't run over a process and just plot data.",
                        default=False)
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Run with debugging info.",
                        default=False)
    parser.add_argument("-r", "--rate", type=float,
                        help="Polling rate for process.", default=0.1)
    parser.add_argument("-i", "--pid", type=int,
                        help="Process id if not using watch.pid",
                        default=None)
    parser.add_argument('rest', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s ==> %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(level=logging.FATAL)

    # TODO:
    # Cleaner way to check if we want to delete the watch pid
    # or use a file instead of a default file or number
    try:
        os.remove('watch.pid')
    except:
        pass

    nowtime = datetime.now().strftime("%m-%d-%Y-%H:%M:%S")

    # Make out output stats csv name
    if args.outfile is not None:
        outfile = args.outfile
    elif args.tag is not None:
        outfile = f'{args.tag}_stats_{nowtime}.csv'
    else:
        outfile = f'stats_{nowtime}.csv'

    logging.info(f'Saving csv to {outfile}')
    logging.info(f'Using tag {args.tag}')
    logging.info(f'Command: {args.rest}')

    # pid = os.spawnlp(os.P_NOWAIT, args.rest[0], *args.rest)
    if args.rest:
        pid = os.spawnlp(os.P_NOWAIT, args.rest[0], *args.rest)
    else:
        pid = args.pid

    # Skip running if we just want to plot
    if not args.just_plot:
        runner(pid=pid, outfile=outfile, poleRate=args.rate)

    # TODO:
    # Need to think about the logic more to clean this up
    # Make sure we want to plot and running plotting
    if not args.no_plot:
        pass
    elif args.just_plot:
        plotter(infile=args.infile,
                tag=f"{args.tag}_{nowtime}" if args.tag is not None else None)
    else:
        plotter(infile=outfile,
                tag=f"{args.tag}_{nowtime}" if args.tag is not None else None)
