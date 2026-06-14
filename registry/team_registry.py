class TeamRegistry:

    def __init__(self):

        self.teams = {}

    def register(
        self,
        name,
        team
    ):

        self.teams[name] = team

    def get(self, name):

        return self.teams.get(name)

    def list(self):

        return list(
            self.teams.keys()
        )