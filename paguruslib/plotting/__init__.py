try:
    import matplotlib  # noqa
    matplotlib.use('agg')  # noqa
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    import sys
    print("Error: Install pandas and matplotlib to plot!", file=sys.stderr)


def cpuPlot(df, tag):
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
    plt.clf()

def memPlot(df, tag):
    df['mem_rss'] = df['mem_rss'] * 1e-9
    df['mem_rss'].plot(label="Raw memory usage")
    df['mem_rss'].rolling('60s').mean().plot(
        label="Average usage (1m)")
    df['mem_rss'].rolling('120s').mean().plot(
        label="Average usage (2m)")
    plt.title(f"memory usage {tag}")
    plt.ylabel("memory usage [MB]")
    plt.xlabel("time")
    lgn = plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    if tag is None:
        plt.savefig("mem.png")
    else:
        plt.savefig(f"{tag}_mem.png",
                    bbox_extra_artists=[lgn],
                    bbox_inches='tight')

    plt.clf()