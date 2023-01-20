import json
import os
import re
from typing import List, Iterator, Tuple, Set, Dict, Union

import dgl
import numpy as np
import torch
from html_to_json_enhanced import iterate
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from dgl import DGLGraph

from models.edge import Edge
from models.node import Node


class GraphLoader(object):
    def __init__(self, data_path: str = None, file_pattern: str = None, body_only: bool = True,
                 embed_walk_length: int = 5):
        # settings
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.file_pattern = file_pattern or r'\.json$'
        self.body_only = body_only
        self.embed_walk_length = embed_walk_length
        self.available_feature_keys = [
            'tag',
            'id',
            'class',
        ]

        # data
        self.nodes: List[Node] = []
        self.nodes_ids: List[int] = []
        self.nodes_ids_map: Dict[str, int] = {}
        self.nodes_features: List[Dict[str, int]] = []
        self.edges: List[Edge] = []
        self.graphs_id_file_map: Dict[int, str] = {}

        # encoders
        self.nodes_features_enc = DictVectorizer()
        self.node_ids_enc = LabelEncoder()

        # tensors
        self.nodes_ids_tensor = torch.LongTensor()
        self.nodes_features_tensor = torch.LongTensor()
        self.edges_source_tensor = torch.LongTensor()
        self.edges_target_tensor = torch.LongTensor()
        self.nodes_embedded_tensor = torch.LongTensor()

        # graph
        self.g_dgl = DGLGraph()

    def iter_all_json_file_paths(self) -> Iterator[str]:
        if os.path.isdir(self.data_path):
            for root, dirs, files in os.walk(self.data_path):
                for file in files:
                    if re.search(self.file_pattern, file) is not None:
                        yield os.path.join(root, file)
        else:
            yield self.data_path

    def load_graph_data(self):
        # iterate files
        for graph_id, filename in enumerate(self.iter_all_json_file_paths()):
            self._load_graph_data(self.get_nodes_json_data(filename), graph_id)
            self.graphs_id_file_map[graph_id] = filename

        # encode node ids
        self.nodes_ids = self.node_ids_enc.fit_transform(
            np.array([node.graph_node_id for node in self.nodes]).reshape(-1, 1)
        )

        # node ids map
        self.nodes_ids_map = {node.graph_node_id: node_id for node, node_id in zip(self.nodes, self.nodes_ids)}

    def get_nodes_json_data(self, filename: str) -> List[dict]:
        with open(filename) as f:
            json_data = json.loads(f.read())

        # by default html as root
        root = json_data

        # if body only
        if self.body_only:
            arr = [c for c in root.get('_children') if c.get('_tag') == 'body']
            if len(arr) > 0:
                root = arr[0]
            else:
                raise Exception('No body tag found')

        return list(iterate(root))

    def _load_graph_data(self, nodes_json_data: List[dict], graph_id: int):
        for i, node_json_data in enumerate(nodes_json_data):
            # node
            node = self._get_node(node_json_data, graph_id)

            # add to all nodes
            self.nodes.append(node)

            # edge
            edge = self._get_edge(node)

            # add to all edges
            self.edges.append(edge)

            # add to all node features
            self.nodes_features.append(node.features_dict)

    def _get_node(self, node_json_data: dict, graph_id: int) -> Node:
        node_id = node_json_data.get('_id')
        parent_id = node_json_data.get('_parent')

        # node
        node = Node({
            'id': node_id,
            'parent_id': parent_id,
            'graph_id': graph_id,
            'features': self._get_node_features(node_json_data),
        })

        return node

    @staticmethod
    def _get_edge(node: Node) -> Edge:
        return Edge({
            'source': node.graph_parent_id,
            'target': node.graph_node_id,
        })

    @staticmethod
    def _get_node_features(node_json_data: dict) -> List[Tuple[str, str]]:
        # features
        features = [('tag', node_json_data.get('_tag'))]

        attributes = node_json_data.get('_attributes')
        if attributes is not None:
            for key, value in attributes.items():
                if isinstance(value, list):
                    for v in value:
                        features.append((key, v))
                else:
                    features.append((key, value))

        return features

    def load_tensors(self):
        # nodes tensors
        self.nodes_ids_tensor = torch.LongTensor(self.nodes_ids)
        features = self.nodes_features_enc.fit_transform(self.nodes_features).todense()
        self.nodes_features_tensor = torch.tensor(data=features, dtype=torch.float32, requires_grad=True)

        # edges tensors
        self.edges_source_tensor = self.nodes_ids_tensor
        node_parent_ids = np.array([self.nodes_ids_map.get(n.graph_parent_id) or 0 for n in self.nodes]).astype(int)
        self.edges_target_tensor = torch.LongTensor(node_parent_ids)

    def load_dgl_graph(self):
        self.g_dgl = dgl.graph((self.edges_source_tensor, self.edges_target_tensor))
        self.g_dgl.ndata['feat'] = self.nodes_features_tensor

        print(self.g_dgl.local_var())

    def load_embeddings(self):
        # embedded nodes tensor
        self.nodes_embedded_tensor = dgl.sampling.node2vec_random_walk(
            self.g_dgl,
            self.nodes_ids_tensor,
            p=1,
            q=1,
            walk_length=self.embed_walk_length,
        )

    def run(self):
        self.load_graph_data()
        self.load_tensors()
        self.load_dgl_graph()
        self.load_embeddings()

    @property
    def graph_ids(self) -> List[str]:
        return list(set(map(lambda n: n.graph_id, self.nodes)))

    def get_node_ids_by_graph_id(self, graph_id) -> List[int]:
        node_ids = np.array([n.graph_node_id for n in self.nodes if n.graph_id == graph_id]).reshape(-1, 1)
        return self.node_ids_enc.transform(node_ids)

    def get_node_by_id(self, id: int) -> Union[Node, None]:
        for node in self.nodes:
            if node.id == id:
                return node

    def get_nodes_by_ids(self, ids: List[int]) -> List[Node]:
        return [n for n in self.nodes if n.id in ids]

    @property
    def _unique_features_idx(self):
        # features counts vector
        features_counts = self.nodes_features_tensor.detach().numpy().sum(axis=0)

        # indexes of features each of which is associated to only one node
        unique_features_idx = np.where(features_counts == 1)

        return unique_features_idx

    @property
    def _available_features_idx(self):
        available_features = [f for f in self.nodes_features_enc.feature_names_
                              if f.split('=')[0] in self.available_feature_keys]
        available_features_mask = np.isin(loader.nodes_features_enc.feature_names_, np.array(available_features))
        available_features_idx = np.argwhere(available_features_mask).T

        return available_features_idx

    @property
    def unique_node_features(self):
        unique_available_features_idx = np.intersect1d(self._unique_features_idx, self._available_features_idx)
        unique_available_features = np.array(loader.nodes_features_enc.feature_names_)[unique_available_features_idx]

        return unique_available_features


if __name__ == '__main__':
    # data_dir_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/quotes.toscrape.com'
    data_path = '/Users/marvzhang/projects/tikazyq/auto-html/data/quotes.toscrape.com/json/http___quotes_toscrape_com_.json'
    loader = GraphLoader(data_path)
    loader.run()
