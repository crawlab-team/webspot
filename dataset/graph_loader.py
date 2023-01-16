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
    def __init__(self, data_path: str = None, file_pattern: str = None, body_only: bool = True,
                 embed_walk_length: int = 5):
        # settings
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.file_pattern = file_pattern or r'\.json$'
        self.body_only = body_only
        self.embed_walk_length = embed_walk_length

        # data
        self.nodes: List[Node] = []
        self.nodes_ids: List[int] = []
        self.nodes_ids_map: Dict[str, int] = {}
        self.nodes_features: List[Dict[str, int]] = []
        self.edges: List[Edge] = []
        self.graphs_id_file_map: Dict[int, str] = {}

        # encoders
        self.feat_enc = DictVectorizer()
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

        if self.body_only:
            if json_data.get('html') is None \
                    or len(json_data.get('html')) == 0 \
                    or json_data.get('html')[0].get('body') is None \
                    or len(json_data.get('html')[0].get('body')) == 0:
                raise Exception('html.body is empty')
            body = json_data['html'][0].get('body')[0]
            elements = list(iterate(body))
            return elements
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
        self.nodes_ids_tensor = torch.LongTensor(self.nodes_ids)
        features = self.feat_enc.fit_transform(self.nodes_features).todense()
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


if __name__ == '__main__':
    # data_dir_path = '/Users/marvzhang/projects/crawlab-team/auto-html/data/quotes.toscrape.com'
    data_dir_path = '/Users/marvzhang/projects/crawlab-team/auto-html/data/quotes.toscrape.com/json/http___quotes_toscrape_com_.json'
    loader = GraphLoader(data_dir_path)
    loader.run()
