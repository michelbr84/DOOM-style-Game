import json
import os

class ScoreManager:
    def __init__(self, file_path='scores.json'):
        self.file_path = file_path
        self.scores = self.load_scores()

    def load_scores(self):
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_scores(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.scores, f)

    def add_win(self, username):
        if username not in self.scores:
            self.scores[username] = {'wins': 0, 'losses': 0}
        self.scores[username]['wins'] += 1
        self.save_scores()

    def add_loss(self, username):
        if username not in self.scores:
            self.scores[username] = {'wins': 0, 'losses': 0}
        self.scores[username]['losses'] += 1
        self.save_scores()

    def get_score(self, username):
        if username not in self.scores:
            return {'wins': 0, 'losses': 0}
        return self.scores[username]
