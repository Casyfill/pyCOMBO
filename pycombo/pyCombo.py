#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import
from io import TextIOWrapper

# import subprocess
# import os
import logging
import tempfile
from pathlib import Path
from typing import Optional
import _combo as comboCPP

__author__ = "Philipp Kats"
__copyright__ = "Philipp Kats"
__license__ = "fmit"

__all__ = ["getComboPartition", "modularity"]
logger = logging.getLogger(__name__)


def _check_repr(G):
    if type(G).__name__ not in {"Graph", "MultiDiGraph"}:
        raise ValueError(
            f"require networkx graph as first parameter, got `{type(G).__name__}`"
        )

    if len(G) == 0:
        raise ValueError("Graph is empty")


def _fileojb_write_graph(f: TextIOWrapper, G, weight: Optional[str] = None) -> dict:
    """write Graph to file as .net Network text file
    Returns dictionary of Nodes
    """
    nodenum, nodes = {}, {}

    f.write(f"*Vertices {len(G.nodes())}\n")
    for i, n in enumerate(G.nodes()):
        f.write(f'{i} "{n}"\n')
        nodenum[n] = i
        nodes[i] = n

    if G.is_directed():
        f.write("*Arcs\n")
    else:
        f.write("*Edges\n")

    for e in G.edges(data=True):
        # NOTE: potential place for speedup if data=False
        if weight is not None:
            # weight_value =
            f.write(f"{nodenum[e[0]]} {nodenum[e[1]]} {e[2].get(weight, 1)}\n")
        else:
            f.write(f"{nodenum[e[0]]} {nodenum[e[1]]} 1\n")
    f.flush()

    logger.debug(f"Wrote Graph to `{f.name}`")
    return nodes


def getComboPartition(
    G,
    weight_prop: Optional[str] = None,
    max_communities: int = -1,
    modularity_resolution: int = 1,
    num_split_attempts: int = 0,
    fixed_split_step: int = 0,
    random_seed: int = -1,
):
    """
    calculates Combo Partition using Combo C++ script
    all details here: https://github.com/Casyfill/pyCOMBO

    G - NetworkX graph
    max_communities - maximum number of communities. If -1, assume to be infinite
    modularity_resolution - modularity resolution parameter
    weight_prop - graph edges property to use as weights. If None, graph assumed to be unweighted
    num_split_attempts - number of split attempts. If 0, autoadjust this number automatically
    fixed_split_step - step number to apply predifined split. If 0, use only random splits,
        if >0 sets up the usage of 6 fixed type splits on every fixed_split_step
    random_seedd - random seed to use

    #### NOTE: code generates temporary partition file
    """

    _check_repr(G)
    directory = Path(__name__).parent.absolute()

    with tempfile.TemporaryDirectory(dir=directory) as tmpdir:
        with open(f"{tmpdir}/temp_graph.net", "w") as f:
            _ = _fileojb_write_graph(f, G, weight=weight_prop)

        result = comboCPP.execute_from_file(
            graph_path=f.name,
            max_communities=max_communities,
            modularity_resolution=modularity_resolution,
            num_split_attempts=num_split_attempts,
            fixed_split_step=fixed_split_step,
            random_seed=random_seed,
        )

        logger.debug(f"Result: {result}")
        return result
        # stdout, stderr = result
        # # stdout, stderr = out.communicate()
        # logger.debug(f"STDOUT: {stdout}")
        # if stderr is not None:
        #     raise Exception(f"STDERR: {stderr}")  # TODO: setup c++ to throw stderr

        # try:
        #     modularity_ = float(stdout)
        # except Exception as e:
        #     raise Exception(stdout, e)


def modularity(G, partition, key: Optional[str] = None):
    """
    compute network modularity
    for the given partitioning

    G:              networkx graph
    partition:      any partition
    key:            weight attribute

    """
    _check_repr(G)
    assert len(G.nodes()) == len(
        partition.keys()
    ), f"Graph got {len(G.nodes())} nodes, partition got {len(partition.keys())}"
    weighted = key is not None
    nodes = G.nodes()
    # compute node weights
    if G.is_directed():
        w1 = G.out_degree(weight=key)
        w2 = G.in_degree(weight=key)
    else:
        w1 = w2 = G.degree(weight=key)

    # compute total network weight
    if weighted:
        T = 2.0 * sum([edge[2][key] for edge in G.edges(data=True)])
    else:
        T = 2.0 * len(G.edges())

    M = 0  # start accumulating modularity score
    for a in nodes:
        for b in nodes:

            try:
                if partition[a] == partition[b]:  # if belong to the same community
                    # get edge weight
                    if G.has_edge(a, b):
                        if weighted:
                            e = G[a][b][key]
                        else:
                            e = 1
                    else:
                        e = 0
                    # add modularity score for the considered edge
                    M += e / T - w1[a] * w2[b] / (T ** 2)
            except KeyError:
                raise KeyError(a, b, partition, nodes)
    return M
