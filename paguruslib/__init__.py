import logging
from time import sleep
import sys
try:
    import psutil
except ImportError:
    print("Error: Install psutil to get statistics!", file=sys.stderr)

## TODO: Look into gpu stats as well
# try:
#     from pynvml import nvmlInit, NVMLError_LibraryNotFound
#     try:
#         nvmlInit()
#     except NVMLError_LibraryNotFound:
#         print("Error: NVML Library not installed!", file=sys.stderr)
# except ImportError:
#     print("Error: Install pynvml to get GPU statistics!", file=sys.stderr)


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