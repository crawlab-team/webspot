import json
import os
import re
from typing import List, Iterator, Tuple, Set, Dict

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
    # data
    nodes: List[Node] = []
    nodes_ids: List[int] = []
    nodes_ids_map: Dict[str, int] = {}
    nodes_features: List[Dict[str, int]] = []
    edges: List[Edge] = []

    # encoders
    feat_enc = DictVectorizer()
    node_ids_enc = LabelEncoder()

    # tensors
    nodes_ids_tensor: torch.Tensor
    nodes_features_tensor: torch.Tensor
    edges_source_tensor: torch.Tensor
    edges_target_tensor: torch.Tensor

    # graph
    g_dgl: DGLGraph

    def __init__(self, data_dir_path: str = None, file_pattern: str = None, body_only: bool = True):
        # settings
        self.data_dir_path = data_dir_path or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.file_pattern = file_pattern or r'\.json$'
        self.body_only = body_only

    def iter_all_json_file_paths(self) -> Iterator[str]:
        """
        iterate all files with pattern in data_dir_path
        """
        for root, dirs, files in os.walk(self.data_dir_path):
            for file in files:
                if re.search(self.file_pattern, file) is not None:
                    yield os.path.join(root, file)

    def load_graph_data(self):
        # iterate files
        for i, filename in enumerate(self.iter_all_json_file_paths()):
            self._load_graph_data(self.get_nodes_json_data(filename), i)

        # encode node ids
        self.nodes_ids = self.node_ids_enc.fit_transform(
            np.array([node.graph_node_id for node in self.nodes]).reshape(-1, 1).astype(str)
        )

        # node ids map
        self.nodes_ids_map = {node.graph_node_id: node_id for node, node_id in zip(self.nodes, self.nodes_ids)}

    def get_nodes_json_data(self, filename: str) -> List[dict]:
        with open(filename) as f:
            json_data = json.loads(f.read())

        if self.body_only:
            if json_data.get('html') is None \
                    or len(json_data.get('html')) == 0 \
                    or json_data.get('html')[0].get('body') is None \
                    or len(json_data.get('html')[0].get('body')) == 0:
                raise Exception('html.body is empty')
            return list(iterate(json_data['html'][0].get('body')[0]))
        else:
            return list(iterate(json_data))

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
        self.nodes_ids_tensor = torch.LongTensor(self.node_ids_enc.fit_transform(self.nodes_ids))
        features = self.feat_enc.fit_transform(self.nodes_features).todense()
        self.nodes_features_tensor = torch.IntTensor(features)

        # edges tensors
        self.edges_source_tensor = self.nodes_ids_tensor
        node_parent_ids = np.array([self.nodes_ids_map.get(n.graph_parent_id) or 0 for n in self.nodes]).astype(int)
        self.edges_target_tensor = torch.LongTensor(node_parent_ids)

    def load_dgl_graph(self):
        self.g_dgl = dgl.graph((self.edges_source_tensor, self.edges_target_tensor))
        self.g_dgl.ndata['feat'] = self.nodes_features_tensor

        print(self.g_dgl.local_var())

    def run(self):
        self.load_graph_data()
        self.load_tensors()
        self.load_dgl_graph()


if __name__ == '__main__':
    data_dir_path = '/Users/marvzhang/projects/crawlab-team/auto-html/data/quotes.toscrape.com'
    loader = GraphLoader(data_dir_path=data_dir_path)
    loader.run()
