class Field(dict):
    @property
    def name(self):
        return self.get('name')

    @property
    def extract_rule(self):
        return self.get('extract_rule_css')
