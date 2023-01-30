from typing import Tuple, List, Dict, Union


class Node(dict):
    @property
    def id(self) -> int:
        return self.get('id')

    @property
    def parent_id(self):
        return self.get('parent_id')

    @property
    def graph_id(self) -> int:
        return self.get('graph_id')

    @property
    def graph_node_id(self) -> str:
        return f'{self.graph_id}.{self.id}'

    @property
    def graph_parent_id(self) -> str:
        return f'{self.graph_id}.{self.parent_id}'

    @property
    def features(self) -> List[Tuple[str, str]]:
        return self.get('features')

    @property
    def features_dict(self) -> Dict[str, int]:
        return {f'{k}={v}': 1 for k, v in self.features}

    @property
    def feature_tag(self) -> Union[str, None]:
        for k, v in self.features:
            if k == 'tag':
                return v
        return None

    @property
    def feature_classes(self) -> List[str]:
        classes = []
        for k, v in self.features:
            if k == 'class':
                classes.append(v)
        return classes

    @property
    def feature_id(self) -> Union[str, None]:
        for k, v in self.features:
            if k == 'id':
                return v
        return None
