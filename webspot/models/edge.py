class Edge(dict):
    @property
    def source_id(self) -> int:
        return self.get('source_id')

    @source_id.setter
    def source_id(self, value):
        self['source_id'] = value

    @property
    def target_id(self) -> int:
        return self.get('target_id')

    @target_id.setter
    def target_id(self, value):
        self['target_id'] = value
