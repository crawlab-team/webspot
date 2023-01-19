class Stats(dict):
    @property
    def entropy(self) -> float:
        return self.get('entropy')

    @property
    def score(self) -> float:
        return self.get('score')
