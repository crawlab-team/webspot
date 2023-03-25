import json
from typing import List, Tuple, Dict, Optional

import dgl
import html_to_json_enhanced
import networkx as nx
import numpy as np
import torch
from bs4 import BeautifulSoup
from html_to_json_enhanced import iterate
from networkx import DiGraph, dfs_successors
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from dgl import DGLGraph

from webspot.graph.models.node import Node
from webspot.logging import get_logger
from webspot.utils.selector import is_valid_css_selector

logger = get_logger('webspot.graph.graph_loader')

SVG_TAG_NAMES = ['circle', 'clipPath', 'defs', 'ellipse', 'g', 'image', 'line', 'linearGradient',
                 'mask', 'path', 'pattern', 'polygon', 'polyline', 'radialGradient', 'rect',
                 'stop', 'svg', 'text', 'tspan']
ESCAPED_TAG_NAMES = [
    'script',
    'link',
    'meta',
    *SVG_TAG_NAMES,
]


class GraphLoader(object):
    def __init__(
        self,
        html: str,
        json_data: dict,
        body_only: bool = True,
        embed_walk_length: int = 8,
        dfs_depth: int = 8,
    ):
        # settings
        self.body_only = body_only
        self.embed_walk_length = embed_walk_length
        self.available_feature_keys = [
            'tag',
            'id',
            'class',
            'style',
        ]
        self.dfs_depth = dfs_depth

        # data
        self.html = html
        self.json_data = json_data
        self.root_node_json: dict = {}
        self.nodes_: List[Node] = []
        self.nodes_ids: List[int] = []
        self.nodes_features: List[Dict[str, int]] = []
        self.edge_nodes: List[Node] = []

        # internals
        self._nodes_dict = None
        self._css_selector_repr_cache = {}
        self._unique_node_feature_id_dict: Optional[dict] = None
        self._nodes_texts: Optional[List[str]] = None
        self._nodes_ids_idx_dict = None
        self._soup: Optional[BeautifulSoup] = None
        self._g_nx: Optional[DiGraph] = None

        # encoders
        self.nodes_features_enc = DictVectorizer()
        self.node_ids_enc = LabelEncoder()

        # tensors
        self.nodes_ids_tensor = torch.LongTensor()
        self.nodes_features_tensor = torch.LongTensor()
        self.edges_source_tensor = torch.LongTensor()
        self.edges_target_tensor = torch.LongTensor()
        self.nodes_embedded_tensor = torch.LongTensor()
        self.nodes_text_length_tensor = torch.LongTensor()

        # vectors
        self.nodes_text_length_vec: Optional[np.ndarray] = None
        self.nodes_full_text_length_vec: Optional[np.ndarray] = None

        # graph
        self.g_dgl: Optional[DGLGraph] = None

    @property
    def nodes_dict(self):
        if self._nodes_dict:
            return self._nodes_dict
        self._nodes_dict = {n.id: n for n in self.nodes_}
        return self._nodes_dict

    @property
    def nodes_ids_idx_dict(self):
        if self._nodes_ids_idx_dict:
            return self._nodes_ids_idx_dict
        self._nodes_ids_idx_dict = {n.id: i for i, n in enumerate(self.nodes_)}
        return self._nodes_ids_idx_dict

    @property
    def g_nx(self) -> nx.DiGraph:
        if self._g_nx:
            return self._g_nx
        self._g_nx = DiGraph(self.g_dgl.to_networkx())
        return self._g_nx

    def get_nodes_json_data_by_filename(self, filename: str) -> (List[dict], dict):
        with open(filename) as f:
            json_data = json.loads(f.read())
        return self.get_nodes_json_data(json_data)

    def get_nodes_json_data(self, json_data: str) -> (List[dict], dict):
        # by default html as root
        root = json_data

        # if body only
        if self.body_only:
            arr = [c for c in root.get('_children') if c.get('_tag') == 'body']
            if len(arr) > 0:
                root = arr[0]
            else:
                raise Exception('No body tag found')

        return list(iterate(root)), root

    def _load_graph_data(self, nodes_json_data: List[dict]):
        for i, node_json_data in enumerate(nodes_json_data):
            # node
            node = self._get_node(node_json_data)

            # skip escaped tags
            if node.tag in ESCAPED_TAG_NAMES:
                continue

            # add to all nodes
            self.nodes_.append(node)

            # add to all node features
            # self.nodes_features.append(node.features_dict)
            self.nodes_features.append({k: v for k, v in node.features_dict.items()
                                        if k.split('=')[0] in self.available_feature_keys
                                        })

    def _get_node(self, node_json_data: dict) -> Node:
        node_id = node_json_data.get('_id')
        parent_id = node_json_data.get('_parent')

        # node
        node = Node({
            'id': node_id,
            'parent_id': parent_id,
            'features': self._get_node_features(node_json_data),
            'text': self._get_node_text(node_json_data),
        })

        return node

    @staticmethod
    def _get_node_features(node_json_data: dict) -> List[Tuple[str, str]]:
        # tags
        features = [('tag', node_json_data.get('_tag'))]

        # attributes
        attributes = node_json_data.get('_attributes')
        if attributes is not None:
            for key, value in attributes.items():
                if isinstance(value, list):
                    for v in value:
                        features.append((key, v))
                else:
                    features.append((key, value))

        return features

    @staticmethod
    def _get_node_text(node_json_data: dict) -> Optional[str]:
        if node_json_data.get('_text') is not None:
            return node_json_data.get('_text')

        elif node_json_data.get('_texts') is not None:
            return ' '.join(node_json_data.get('_texts'))

        else:
            return

    def load_graph_data(self):
        # get list data and root node
        self.json_data = html_to_json_enhanced.convert_html.convert(self.html, with_id=True)
        list_data, self.root_node_json = self.get_nodes_json_data(self.json_data)

        # load graph data
        self._load_graph_data(list_data)

        # encode node ids
        self.nodes_ids = self.node_ids_enc.fit_transform(
            np.array([node.id for node in self.nodes_]).reshape(-1, 1)
        )

    def load_tensors(self):
        # nodes tensor
        encoded_nodes = self.node_ids_enc.transform([n.id for n in self.nodes_])
        self.nodes_ids_tensor = torch.LongTensor(encoded_nodes)

        # nodes features tensor
        features = self.nodes_features_enc.fit_transform(self.nodes_features).todense()
        self.nodes_features_tensor = torch.tensor(data=features, dtype=torch.float32, requires_grad=True)

        # edge nodes
        self.edge_nodes = [n for n in self.nodes_ if self.nodes_dict.get(n.parent_id) is not None]

        # edges tensors
        encoded_source = self.node_ids_enc.transform([n.parent_id for n in self.edge_nodes])
        encoded_target = self.node_ids_enc.transform([n.id for n in self.edge_nodes])
        self.edges_source_tensor = torch.LongTensor(encoded_source)
        self.edges_target_tensor = torch.LongTensor(encoded_target)

    def load_dgl_graph(self):
        self.g_dgl = dgl.graph((self.edges_source_tensor, self.edges_target_tensor))

    def load_embeddings(self):
        # embedded nodes tensor
        self.nodes_embedded_tensor = dgl.sampling.node2vec_random_walk(
            g=self.g_dgl,
            nodes=self.nodes_ids_tensor,
            p=1,
            q=1,
            walk_length=self.embed_walk_length,
        )

    def load_soup(self):
        self._soup = BeautifulSoup(self.html, 'html.parser')

    def load_texts(self):
        self._nodes_texts = [n.text for n in self.nodes_]
        self.nodes_text_length_vec = np.array([len(t or []) for t in self._nodes_texts])

    def run(self):
        self.load_graph_data()
        self.load_tensors()
        self.load_dgl_graph()
        self.load_embeddings()
        self.load_soup()
        self.load_texts()

    @property
    def nodes(self):
        return np.array(self.nodes_)

    def get_node_by_id(self, id: int) -> Optional[Node]:
        return self.nodes_dict.get(id)

    def get_nodes_by_ids(self, ids: List[int]) -> List[Node]:
        return [self.get_node_by_id(id) for id in ids]

    def get_node_children_recursive_by_id(self, id: int) -> List[Node]:
        idx = self.node_ids_enc.transform([id])[0]
        child_nodes_idx = self.get_node_children_idx_recursive_by_id(id)
        child_ids = self.node_ids_enc.inverse_transform([nid for nid in child_nodes_idx if nid != idx])
        return self.get_nodes_by_ids(child_ids)

    def get_node_children_idx_recursive_by_id(self, id: int) -> np.ndarray:
        idx = self.node_ids_enc.transform([id])[0]
        return self.get_node_children_idx_recursive_by_idx(idx)

    def get_node_children_idx_recursive_by_idx(self, idx: int) -> np.ndarray:
        successors = dfs_successors(G=self.g_nx, source=idx, depth_limit=self.dfs_depth)
        child_nodes_idx = [item for sublist in successors.values() for item in sublist]
        return np.array(list(child_nodes_idx))

    def get_node_text_length(self, n: Node, max_length: int = 1024) -> int:
        selector = self.get_node_css_selector_path(n)
        el = self._soup.select_one(selector)
        if el is None:
            return 0
        return min(len(el.text), max_length)

    def get_node_children_by_id(self, id: int) -> List[Node]:
        return [n for n in self.nodes_ if n.parent_id == id]

    @property
    def unique_features_idx(self):
        # features counts vector
        features_counts = self.nodes_features_tensor.detach().numpy().sum(axis=0)

        # indexes of features each of which is associated to only one node
        unique_features_idx = np.where(features_counts == 1)

        return unique_features_idx

    @property
    def available_features_idx(self):
        available_features = [f for f in self.nodes_features_enc.feature_names_
                              if f.split('=')[0] in self.available_feature_keys]
        available_features_mask = np.isin(self.nodes_features_enc.feature_names_, np.array(available_features))
        available_features_idx = np.argwhere(available_features_mask).T

        return available_features_idx

    @property
    def unique_available_features_idx(self):
        return np.intersect1d(self.unique_features_idx, self.available_features_idx)

    @property
    def unique_node_feature_pairs_idx(self):
        """
        2-dimensional node-feature pairs index
        """
        nodes_feat = self.nodes_features_tensor.detach().numpy()
        uniq_avail_nodes_feat = np.zeros(nodes_feat.shape)
        uniq_idx = self.unique_available_features_idx
        uniq_avail_nodes_feat[:, uniq_idx] = nodes_feat[:, uniq_idx]
        return np.argwhere(uniq_avail_nodes_feat > 0)

    @property
    def unique_node_feature_pairs(self):
        nodes = self.nodes[self.unique_node_feature_pairs_idx[:, 0]].tolist()
        feats = np.array(self.nodes_features_enc.feature_names_)[self.unique_node_feature_pairs_idx[:, 1]].tolist()
        return [(n, f) for n, f in zip(nodes, feats)]

    @property
    def unique_node_feature_id_dict(self) -> Dict[int, str]:
        if self._unique_node_feature_id_dict is not None:
            return self._unique_node_feature_id_dict
        self._unique_node_feature_id_dict = {n.id: f for n, f in self.unique_node_feature_pairs}
        return self._unique_node_feature_id_dict

    def _get_node_previous_siblings(self, node: Node) -> List[Node]:
        return [n for n in self.nodes_ if n.parent_id == node.parent_id
                and n.id < node.id
                and n.feature_tag == node.feature_tag]

    def _get_node_previous_siblings_with_classes(self, node: Node) -> List[Node]:
        node_feature_classes_set = set(node.feature_classes)
        return [n for n in self.nodes_ if n.parent_id == node.parent_id
                and n.id < node.id
                and n.feature_tag == node.feature_tag
                and node_feature_classes_set.issubset(set(n.feature_classes))]

    def _is_node_last_child(self, node: Node) -> bool:
        parent = self.get_node_by_id(node.parent_id)
        children = self.get_node_children_by_id(parent.id)
        return node.id == children[-1].id

    def get_node_css_selector_repr(self, node: Node, numbered: bool = True, no_id: bool = False) -> str:
        if numbered:
            return self._get_node_css_selector_repr(node, numbered, no_id)

        if self._css_selector_repr_cache.get(node.id):
            return self._get_node_css_selector_repr(node, numbered, no_id)

        self._css_selector_repr_cache[node.id] = self._get_node_css_selector_repr(node, numbered, no_id)
        return self._css_selector_repr_cache.get(node.id)

    def _get_node_css_selector_repr(self, node: Node, numbered: bool = True, no_id: bool = False) -> str:
        # id
        if node.feature_id is not None and not no_id and is_valid_css_selector(f'#{node.feature_id}'):
            return f'{node.feature_tag}#{node.feature_id}'

        # class
        elif len(node.feature_classes) > 0 and is_valid_css_selector('.'.join(node.feature_classes)):
            if numbered:
                previous_siblings = self._get_node_previous_siblings_with_classes(node)
                length = len(previous_siblings) + 1
                if length > 1:
                    if self._is_node_last_child(node):
                        return f'{node.feature_tag}.{".".join(node.feature_classes)}:last-child'
                    return f'{node.feature_tag}.{".".join(node.feature_classes)}:nth-of-type({length})'
            return f'{node.feature_tag}.{".".join(node.feature_classes)}'

        # tag
        else:
            if numbered:
                length = len(self._get_node_previous_siblings(node)) + 1
                if length > 1:
                    if self._is_node_last_child(node):
                        return f'{node.feature_tag}:last-child'
                    return f'{node.feature_tag}:nth-of-type({length})'
            return f'{node.feature_tag}'

    @staticmethod
    def _get_node_css_selector_repr_from_feature(feat: str):
        k, v = feat.split('=')
        if k == 'tag':
            return v
        elif k == 'class':
            return f'.{v}'
        else:
            return f'[{k}="{v}"]'

    def get_node_css_selector_path(self, node: Node, root_id: int = None, numbered: bool = True,
                                   no_id: bool = False) -> str:
        # return if no parent
        if node.parent_id is None:
            return self.get_node_css_selector_repr(node=node, numbered=numbered, no_id=no_id)

        # css selector path
        path = [self.get_node_css_selector_repr(node=node, numbered=numbered, no_id=no_id)]

        # iterate node parent until reaching end condition
        while node.parent_id is not None:
            # parent
            parent = self.get_node_by_id(node.parent_id)

            # end if parent is root
            if root_id is not None and parent.id == root_id:
                break

            # end if no parent
            if parent is None:
                break

            # end if parent node is unique-feature
            if not no_id and self.unique_node_feature_id_dict.get(parent.id) is not None:
                feat = self.unique_node_feature_id_dict.get(parent.id)
                path.insert(0, self.get_node_css_selector_repr(parent, numbered=numbered, no_id=no_id))
                break

            # add to path
            parent_path = self.get_node_css_selector_repr(parent, numbered=numbered, no_id=no_id)
            path.insert(0, parent_path)

            # set node to its parent
            node = parent

        return ' > '.join(path)
