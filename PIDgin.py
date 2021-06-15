#!/usr/bin/env python3
import argparse
import psutil
from time import sleep, strftime
import os
import logging

global plotting
try:
    import matplotlib  # noqa
    matplotlib.use('agg')  # noqa
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    plotting = True
except ImportError:
    plotting = False


logging.basicConfig(
    format='%(asctime)s %(levelname)s ==> %(message)s', level=logging.INFO)


def getProcessPid(pidfile: str = "watch.pid") -> int:
    """
    Get a process id that was saved in a file.

    On unix systems you can get the pid from the last
    run command with the `$!` environment variable
    which can be saved to a file like:

    `./test_program &; echo $! > watch.pid`

    Parameters:
    pidfile (str): File location of pid.

    Returns:
    int: process pid from file
    """

    # Wait for ~5 minutes (300 seconds)
    for _ in range(300):
        # Try to open the file
        try:
            with open(pidfile) as pid:
                pid = int(pid.readlines()[0].strip())
                logging.info(f"Getting running process {pid}")
                return pid
        # If file not found wait for a second and try again
        except FileNotFoundError:
            sleep(1)

    # Should only get here if we've exasted our ~5 minute wait time
    logging.fatal("Could not attatch to process after 5 minutes...")
    logging.fatal("Quitting PIDgin process")
    exit(100)


def getProcess(pid: int) -> psutil.Process:
    """
    Get psutil process object from the pid.

    Parameters:
    pid (int): pid you want to get object of.

    Returns:
    psutil.Process: Process object from psutils
    """
    try:
        return psutil.Process(pid)
    except psutil.NoSuchProcess:
        logging.fatal("Could not attatch to process...")
        logging.fatal("psutil.NoSuchProcess")
        exit(200)


def runner(pid: int = None, outfile: str = "stats.csv", poleRate: float = 0.1):
    """
    Runs while your executable is still running and logs info
    about running process to a csv file.

    Args:
        pid(int, optional): PID of the process you want to atatch to. Defaults to None.
        outfile (str, optional): output filename. Defaults to "stats.csv".
        poleRate (float, optional): Time to sleep before getting new data. Defaults to 0.1.
    """

    # If we're not given a pid get one from "watch.pid" file
    if pid is None:
        pid = getProcessPid()

    # Get our processing object based on the pid
    proc = getProcess(pid)
    logging.info(f'{proc.cmdline()}')

    stats_file = open(outfile, "w")
    # TODO make a good header for extra info like:
    # proc.cmdline() num_threads, etc.

    stats_file.write("{},{},{},{},{},{},{}\n".format(
        "datetime", "num_threads", "cpu_percent", "memory_info", "num_fds", "read_bytes", "write_bytes"
    ))

    # Keep pulling data from the process while it's running
    while proc.is_running():
        # In a rare case at the end of the job running
        # we can get that the process is_running to be true
        # but stops while extracting a parameter.
        # So I get all the data as a dict and break if we have any issues
        try:
            pData = proc.as_dict()
            # Add new line to the file with relevant data
            stats_file.write("{},{},{},{},{},{},{}\n".format(
                strftime("%Y-%m-%d %H:%M:%S"),
                pData['num_threads'],
                pData['cpu_percent'],
                pData['memory_info'][0],
                pData['num_fds'],
                pData['io_counters'][2] if 'io_counters' in pData else np.nan,
                pData['io_counters'][3] if 'io_counters' in pData else np.nan,
            ))
        except:
            # Breaks out of just the loop and not the function
            break
        # Sleep for a number of seconds before going to the next loop
        sleep(poleRate)

    # Finally we close the file.
    stats_file.close()


def plotter(infile: str = "stats.csv"):
    """
    Plot the results from the runner step. 
    It can be done after the fact with `-j` option to just plot.

    Args:
        infile (str, optional): Input filename for csv. Defaults to "stats.csv".
    """

    # Check that we have
    if not plotting:
        logging.fatal("Plotting failed...")
        logging.fatal(
            """
            For plots make sure you have
            matplotlib, pandas, and numpy installed.
            """
        )
        exit(300)

    logging.info("Running plotting.")
    df = pd.read_csv(infile,
                     index_col=[0],
                     dtype={0: str, 1: np.float16, 2: float,
                            3: float, 4: float, 5: float},
                     parse_dates=[0])

    df['cpu_percent'].plot()
    df['cpu_percent'].rolling('60s').mean().plot()
    df['cpu_percent'].rolling('120s').mean().plot()
    plt.savefig("cpu.png")

    plt.clf()
    df['memory_info'] = df['memory_info'] / 1024**3
    df['memory_info'].plot(label="Raw memory usage")
    df['memory_info'].rolling('60s').mean().plot(
        label="Average usage (1m)")
    df['memory_info'].rolling('120s').mean().plot(
        label="Average usage (2m)")
    plt.legend()
    plt.savefig("mem.png")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfile", type=str,
                        help="Output file name for csv. Also used for the input of the plotting funtion.",
                        default="stats.csv")
    parser.add_argument("-np", "--no-plot", action="store_false",
                        help="Plot the data.", default=True)
    parser.add_argument("-j", "--just-plot", action="store_true",
                        help="Don't run over a process and just plot data.",
                        default=False)
    parser.add_argument("-r", "--rate", type=float,
                        help="Polling rate for process.", default=0.1)
    parser.add_argument("-i", "--pid", type=int,
                        help="Process id if not using watch.pid",
                        default=None)
    args = parser.parse_args()

    # TODO:
    # Cleaner way to check if we want to delete the watch pid
    # or use a file instead of a default file or number
    try:
        os.remove('watch.pid')
    except:
        pass

    # Skip running if we just want to plot
    if not args.just_plot:
        runner(pid=args.pid, outfile=args.outfile, poleRate=args.rate)

    # TODO:
    # Need to think about the logic more to clean this up

    # Make sure we want to plot and running plotting
    if not args.no_plot:
        pass
    elif args.just_plot:
        plotter(infile=args.outfile)
    else:
        plotter(infile=args.outfile)
