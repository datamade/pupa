from collections import defaultdict


class CyclicGraphError(ValueError):
    """
    This exception is raised if the graph is Cyclic (or rather, when the
    sorting algorithm *knows* that the graph is Cyclic by hitting a snag
    in the top-sort)
    """
    pass


class Network(object):
    """
    This object (the `Network` object) handles keeping track of all the
    graph's nodes, and links between the nodes.

    The `Network' object is mostly used to topologically sort the nodes,
    to handle dependency resolution.
    """

    def __init__(self):
        self.nodes = []
        self.edges = defaultdict(list)

    def add_node(self, node):
        """ Add a node to the graph (with no edges) """
        self.nodes.append(node)

    def add_edge(self, fro, to):
        """
        Add an edge from node `fro` to node `to`. For instance, to say that
        `foo` depends on `bar`, you'd say::

            `network.add_edge('foo', 'bar')`
        """

        if fro not in self.nodes:
            self.add_node(fro)

        if to not in self.nodes:
            self.add_node(to)

        self.edges[fro].append(to)

    def leaf_nodes(self):
        """
        Return an interable of nodes with no edges pointing at them. This is
        helpful to find all nodes without dependencies.
        """
        deps = set([
            item for sublist in self.edges.values() for item in sublist
        ])
        return (x for x in self.nodes if x not in deps)

    def prune_node(self, node):
        """
        remove node `node` from the network (including any edges that may
        have been pointing at `node`).
        """
        self.nodes = [x for x in self.nodes if x != node]
        if node in self.edges:
            self.edges.pop(node)
        for fro, connections in self.edges.items():
            if node in self.edges[fro]:
                self.edges[fro] = [x for x in connections if x != node]

    def sort(self):
        """
        Return an iterable of nodes, toplogically sorted to correctly import
        dependencies before leaf nodes.
        """
        while self.nodes != []:
            iterated = False
            for node in self.leaf_nodes():
                iterated = True
                self.prune_node(node)
                yield node
            if not iterated:
                raise CyclicGraphError("Sorting has found a cyclic graph.")
