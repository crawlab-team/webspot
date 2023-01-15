import json
import os
import re
from typing import List, Iterator, Tuple, Set

from html_to_json_enhanced import iterate
from sklearn.preprocessing import OneHotEncoder
import numpy as np

from models.edge import Edge
from models.node import Node


class GraphLoader(object):
    def __init__(self, data_dir_path: str = None, file_pattern: str = None, body_only: bool = True):
        # settings
        self.data_dir_path = data_dir_path or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.file_pattern = file_pattern or r'\.json$'
        self.body_only = body_only

        # data
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.node_features: Set[str] = set()

        # feature encoder
        self.feat_enc = OneHotEncoder()

        # global node id
        self._node_id = 0

    def iter_all_json_file_paths(self) -> Iterator[str]:
        """
        iterate all files with pattern in data_dir_path
        """
        for root, dirs, files in os.walk(self.data_dir_path):
            for file in files:
                if re.search(self.file_pattern, file) is not None:
                    yield os.path.join(root, file)

    def load_nodes(self):
        for filename in self.iter_all_json_file_paths():
            self._load_nodes(self.get_nodes_json_data(filename))

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

    def _load_nodes(self, nodes_json_data: List[dict]):
        for i, node_json_data in enumerate(nodes_json_data):
            # node
            node = self._get_node(node_json_data)

            # add to all nodes
            self.nodes.append(node)

            # add to all node features
            for f in node.features_str:
                self.node_features.add(f)

    def _get_node(self, node_json_data: dict) -> Node:
        # node
        node = Node({
            'id': node_json_data.get('_id'),
            'parent_id': node_json_data.get('_parent'),
            'features': self._get_node_features(node_json_data),
        })

        return node

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

    def encode_node_features(self):
        features = np.array(list(self.node_features))
        self.feat_enc.fit(features.reshape(-1, 1))
        print(self.feat_enc.categories_)

    def run(self):
        self.load_nodes()
        self.encode_node_features()


if __name__ == '__main__':
    data_dir_path = '/Users/marvzhang/projects/crawlab-team/auto-html/data/ssr1.scrape.center'
    loader = GraphLoader(data_dir_path=data_dir_path)
    loader.run()
