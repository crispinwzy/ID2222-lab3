import random

def closedBy(wedge, new_edge) -> bool:
    """Check if a wedge would be closed by a edge or not.

    Args:
        wedge (set): A set of two edges.  e.g. {{1,2}, {2,3}}
        new_edge (set): A set of two nodes (int).  e.g. {3,1}
    Returns:
        bool: True if `wedge` and `new_edge` can form a triangle, False otherwise.
    """
    e1, e2 = wedge

    if len(e1 | e2 | new_edge) == 3:
        return True
    else:
        return False

class StreamingTriangles:

    def __init__(self, size_e: int, size_w: int):
        """Initialize an instance

        Args:
            size_e (int): The size of edge_res
            size_w (int): The size of wedge_res
        """
        self.edge_res = [None] * size_e # e.g. [{1,2}]

        self.wedge_res = [None] * size_w # e.g. [ {{1,2}, {2,3}} ]
        self.isClosed = [None] * size_w

        self.total_wedges = 0 # total number of wedges formed by edges in the current edge_res
        self.fraction_of_true = 0 # fraction of true bits in isClosed

        # desired result
        self.estd_transitivity = 0 # kt
        self.estd_triangle_counts = 0 # Tt

    def _update_total_wedges(self):
        """Update the number of wedges formed by edges in the latest edge_res."""
        count = 0

        # traverse all wedges_res
        for wedge in self.wedge_res:
            if wedge is not None:
                edge1, edge2 = wedge
                # for each wedge, if both of edges appears in the edge_res, count+=1
                if edge1 in self.edge_res and edge2 in self.edge_res:
                    count += 1

        self.total_wedges = count

    def _generate_new_wedges(self, new_edge):
        """Generate Nt (a list of all wedges involving new_edge formed only by edges in edge res)

        Args:
            new_wedge (set): A set of two nodes(int).  e.g. {1,2}
        Returns:
            list: a list of wedges. e.g. [{{1,2}, {2,3}}, {5,6},{6,7}]
        """
        Nt = set()

        for edge in self.edge_res:
            if edge is not None:
                if len(new_edge|edge) == 3:
                    Nt.add(frozenset({frozenset(new_edge), frozenset(edge)}))

        return list(Nt)

    def _update_result(self, stream_count):
        """Update `transitivity` and `triangle counts`"""
        true_count = len(list(filter(lambda item: item == True, self.isClosed)))
        self.fraction_of_true = true_count / len(self.isClosed)

        self.estd_transitivity = 3 * self.fraction_of_true
        size_e = len(self.edge_res)
        self.estd_triangle_counts = ((self.fraction_of_true * (stream_count ** 2)) / size_e * (size_e-1)) * self.total_wedges

    def update(self, new_edge, stream_count):
        """Main function that receives a new edge from a streaming and update desired results

        Args:
            new_wedge (set): A set of two nodes(int).  e.g. {1,2}
            stream_count (int): The ID of the stream
        """
        # Check whether any existing wedge would be closed by the new edge
        for i in range(len(self.wedge_res)):
            if self.wedge_res[i] is not None:
                if closedBy(self.wedge_res[i], new_edge):
                    self.isClosed[i] = True

        updated = False

        if stream_count-1 < len(self.edge_res):
            self.edge_res[stream_count-1] = new_edge
            updated = True
        else:
            # reservoir sampling for edge_res
            r = random.randint(0, stream_count-1)
            if r < len(self.edge_res):
                self.edge_res[r] = new_edge
                updated = True

        # if any update of edge_res happens
        if updated:
            self._update_total_wedges()

            # determine new_wedges/Nt
            new_wedges = self._generate_new_wedges(new_edge)

            # reservoir sampling for wedge_res
            if len(new_wedges) > 0:
                for _ in range(0, len(self.wedge_res)):
                    r = random.random()
                    if self.total_wedges == 0 or r <= len(new_wedges) / self.total_wedges:
                        i = random.randint(0, len(self.wedge_res)-1)
                        self.wedge_res[i] = random.choice(new_wedges)
                        self.isClosed[i] = False
                        break
                    else:
                        continue

            # finally update the kt and Tt
            self._update_result(stream_count)

            # log info
            edge_count = len(list(filter(lambda item: item != None, self.edge_res)))
            wedge_count = len(list(filter(lambda item: item != None, self.wedge_res)))
            true_count = len(list(filter(lambda item: item == True, self.isClosed)))
            print('[Updated Stream #{}] transitivity: {}, triangles: {} (edge_res: {}, wedge_res: {}, true: {}, total_wedge: {})'.format(stream_count, self.estd_transitivity, self.estd_triangle_counts, edge_count, wedge_count, true_count, self.total_wedges))
