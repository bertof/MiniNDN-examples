import string

import pandas as pd
import seaborn as snm
import yaml
from matplotlib import pyplot as plt
from pandas import DataFrame

pd.options.display.max_columns = 30
plt.style.use("seaborn")
snm.reset_defaults()


def name_to_id(node):
    return "R" + "".join(filter(lambda c: c in string.digits, node))


def name_to_node_number(node):
    return int("".join(filter(lambda c: c in string.digits, node)))


def parse_topology_data(topology_file):
    with open(topology_file) as f:
        return yaml.full_load(f)


def plot_topology(topology_data):
    topology = DataFrame()
    for group, nodes in topology_data.items():
        if group != "connections" and nodes is not None:
            data = {
                "Node": nodes.keys(),
                "Latitude": map(lambda n: nodes[n]["LAT"], nodes.keys()),
                "Longitude": map(lambda n: nodes[n]["LON"], nodes.keys()),
            }
            df = DataFrame(data)
            df["Type"] = group.rstrip("s").capitalize()
            topology = topology.append(df, sort=False)

    # Plot
    fig, ax = plt.subplots()

    for r in topology_data["connections"]:
        for src, dst in r.items():
            ax.plot(
                topology[topology["Node"].apply(lambda n: n in [src, dst])]["Longitude"],
                topology[topology["Node"].apply(lambda n: n in [src, dst])]["Latitude"],
                c="b",
                label=''
            )

    for name, group in topology.groupby("Type"):
        ax.plot(
            group["Longitude"], group["Latitude"],
            marker="o", linestyle="", ms=10,
            label=name)

    for k, point in topology.iterrows():
        ax.annotate(
            point["Node"],
            point[["Longitude", "Latitude"]],
            xytext=(10, 5),
            textcoords='offset points',
            fontsize=15
        )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.margins(0.33)
    plt.show()



