import geopandas as gpd
import matplotlib
from matplotlib import rcParams
import matplotlib.pyplot as plt
import os
import seaborn as sns
from shapely import wkt

custom_params = {
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'legend.title_fontsize': 10
    # 'text.usetex': True,
    # 'text.latex.preamble': '\\usepackage[libertine]{newtxmath}\n\\usepackage{libertine}'
}

sns.set_theme(
    style='white',
    font='libertine',
    rc=custom_params
)


def plot_station_coverage(stations, path):
    fig, ax = plt.subplots()
    plot_coverage(stations, ax)
    plot_stations(stations, ax)
    plt.show()
    fig.savefig(path, bbox_inches="tight")
    
def plot_topology(links, stations, path):
    
    print(stations)
    print(links)
    
    # stations = stations.to_crs(4326)
    # links = links.to_crs(4326)
    
    # print(stations)
    # print(links)
    
    fig, ax = plt.subplots()
    plot_coverage(stations, ax)
    plot_stations(stations, ax)
    plot_links(links, ax)
    ax.axis('off')
    # plt.xticks(visible=False)
    # plt.yticks(visible=False)
    plt.show()
    fig.savefig(path, bbox_inches="tight")
    
def plot_link_load(loads, stations, path):
    fig, ax = plt.subplots()
    plot_coverage(stations, ax)
    plot_stations(stations, ax)
    plot_loads(loads, ax)
    # plt.show()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close()
    
def plot_connectivity(stations, path):
    fig, ax = plt.subplots()
    coverage = gpd.GeoDataFrame(stations, geometry='coverage')
    
    ax = coverage[coverage['radius'] >= 0].plot(
        color='#ff6600',
        # column='radius',
        ax=ax
    )
    ax = coverage[coverage['radius'] == -1].plot(
        color='#ffe6d5',
        # column='radius',
        ax=ax
    )
    
    ax.axis('off')
    plt.show()
    fig.savefig(path, bbox_inches="tight", dpi=80)

################################################################################
    
def plot_coverage(stations, ax):
    coverage = gpd.GeoDataFrame(stations, geometry='coverage')
    coverage.plot(
        color='lightgray',
        ax=ax
    )

def plot_stations(stations, ax):
    stations.plot(
        color='white',
        marker='2',
        markersize=10,
        ax=ax
    )

def plot_links(links, ax):
    links.plot(
        color='#DD6E2B',
        markersize=10,
        ax=ax
    )
    
def plot_loads(loads, ax):
    # loads[loads['traffic'] == 0].plot(
    #     color='blue',
    #     markersize=10,
    #     ax=ax
    # )
    loads = loads[loads['traffic'] > 0].sort_values('traffic')
    print(loads)
    loads.plot(
        column='traffic',
        cmap='YlOrBr',
        markersize=10,
        # norm=matplotlib.colors.LogNorm(),
        ax=ax
    )
