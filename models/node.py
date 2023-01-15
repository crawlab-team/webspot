from typing import Tuple, List


class Node(dict):
    @property
    def id(self) -> int:
        return self.get('id')

    @id.setter
    def id(self, value):
        self['id'] = value

    @property
    def parent_id(self):
        return self.get('parent_id')

    @parent_id.setter
    def parent_id(self, value):
        self['parent_id'] = value

    @property
    def features(self) -> List[Tuple[str, str]]:
        return self.get('features')

    @features.setter
    def features(self, value):
        self['features'] = value

    @property
    def features_str(self) -> List[str]:
        return [f'{k}={v}' for k, v in self.features]
