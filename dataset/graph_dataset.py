from typing import List

from dgl import DGLGraph
from torch.utils.data import Dataset

from dataset.graph_loader import GraphLoader


class GraphDataset(Dataset):

    def __init__(self, data_path: str = None, file_pattern: str = None, body_only: bool = True):
        super().__init__()

        self.graphs: List[DGLGraph] = []
        self.global_graph_loader = GraphLoader(data_path, file_pattern, body_only)
        self.global_graph_loader.run()

        for graph_id in self.global_graph_loader.graph_ids:
            node_ids = self.global_graph_loader.get_node_ids_by_graph_id(graph_id)
            graph = self.global_graph_loader.g_dgl.subgraph(node_ids)
            # print(graph.local_var())
            self.graphs.append(graph)

    def __len__(self):
        return len(self.graphs)

    def __getitem__(self, index):
        return self.graphs[index]


if __name__ == '__main__':
    data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/quotes.toscrape.com'
    GraphDataset(data_path)
