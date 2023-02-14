from typing import Tuple, List, Dict, Union


class Node(dict):
    @property
    def id(self) -> int:
        return self.get('id')

    @property
    def parent_id(self):
        return self.get('parent_id')

    @property
    def features(self) -> List[Tuple[str, str]]:
        features = []
        for k, v in self.get('features'):
            # skip pseudo-classes
            if k == 'class':
                if ':' in v:
                    continue
            features.append((k, v))
        return features

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

    @property
    def text(self) -> str:
        return self.get('text')

    @property
    def tag(self):
        return self.feature_tag

    @property
    def attrs(self):
        return {k: v for k, v in self.features if k != 'tag'}
