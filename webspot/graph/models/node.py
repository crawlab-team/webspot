import re
from typing import Tuple, List, Dict, Optional


class Node(dict):
    @property
    def id(self) -> int:
        return self.get('id')

    @property
    def parent_id(self):
        return self.get('parent_id')

    @property
    def features(self) -> Tuple[Tuple[str, str]]:
        features: List[Tuple[str, str]] = []
        for k, v in self.get('features'):
            # skip pseudo-classes
            if k == 'class':
                if ':' in v:
                    continue
            features.append((k, v))
        return tuple(features)

    @property
    def features_dict(self) -> Dict[str, int]:
        return {f'{k}={v}': 1 for k, v in self.features}

    @property
    def feature_tag(self) -> Optional[str]:
        for k, v in self.features:
            if k == 'tag':
                return v
        return None

    @property
    def feature_classes(self) -> List[str]:
        classes = []
        for k, v in self.features:
            if k == 'class':
                # css parser cannot parse class starting with a digit
                if re.search(r'^\d', v) is not None:
                    continue
                classes.append(v)
        return classes

    @property
    def feature_id(self) -> Optional[str]:
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
