from flet import *
from pandas import *
from filelock import FileLock

class CreateTask(Container):
    def __init__(self, navigate_to, mutex):
        super().__init__(
            content=Column(
                controls=[
                    TextField(label="Scorer's Name", width=300),
                    Dropdown(
                        label="Competition Type",
                        options=[
                            dropdown.Option("one-to-one"),
                            dropdown.Option("one-to-two"),
                            dropdown.Option("two-to-two"),
                        ],
                        width=300,
                        on_change=self.update_players_fields
                    ),
                    Column([], spacing=5, width=300, visible=False),
                    TextField(label="Match Start Time", width=300),
                    Row(
                        controls=[
                            TextField(label="Starting Score Team 1", width=145),
                            TextField(label="Starting Score Team 2", width=145)
                        ],
                        alignment=MainAxisAlignment.CENTER,
                    ),
                    ElevatedButton(text="Submit Task", on_click=self.submit, width=300),
                    ElevatedButton(text="Back", on_click=self.back, width=300)
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=alignment.center,
            expand=True
        )
        self.name = "Create task"
        self.navigate_to = navigate_to
        self.mutex = mutex
        self.players_fields = self.content.controls[2]
    
    def reset(self):
        self.content.controls[0].value = ""
        self.content.controls[1].value = None
        self.content.controls[3].value = ""
        self.content.controls[4].controls[0].value = ""
        self.content.controls[4].controls[1].value = ""
        self.players_fields.controls.clear()
        self.players_fields.visible = False
    
    def back(self, e):
        self.navigate_to("Referee")
    
    def update_players_fields(self, e):
        competition_type = e.control.value
        self.players_fields.controls.clear()
        
        if competition_type == "one-to-one":
            self.players_fields.controls.append(TextField(label="Player 1 Name", width=300))
            self.players_fields.controls.append(TextField(label="Player 2 Name", width=300))
        elif competition_type == "two-to-two":
            self.players_fields.controls.append(TextField(label="Team 1 - Player 1 Name", width=300))
            self.players_fields.controls.append(TextField(label="Team 1 - Player 2 Name", width=300))
            self.players_fields.controls.append(TextField(label="Team 2 - Player 1 Name", width=300))
            self.players_fields.controls.append(TextField(label="Team 2 - Player 2 Name", width=300))
        elif competition_type == "one-to-two":
            self.players_fields.controls.append(TextField(label="Team 1 - Player 1 Name", width=300))
            self.players_fields.controls.append(TextField(label="Team 2 - Player 1 Name", width=300))
            self.players_fields.controls.append(TextField(label="Team 2 - Player 2 Name", width=300))
        
        self.players_fields.visible = True
        self.page.update()
        
    def submit(self, e):
        scorer_name = self.content.controls[0].value
        competition_type = self.content.controls[1].value
        match_start_time = self.content.controls[3].value
        starting_score_team1 = self.content.controls[4].controls[0].value
        starting_score_team2 = self.content.controls[4].controls[1].value
        
        player_names = [field.value for field in self.players_fields.controls]
        
        competition_data = {
            "ScorerName": scorer_name,
            "CompetitionType": competition_type,
            "Team 1 - Player 1 Name": None,
            "Team 1 - Player 2 Name": None,
            "Team 2 - Player 1 Name": None,
            "Team 2 - Player 2 Name": None,
            "MatchStartTime": match_start_time,
            "StartingScoreTeam1": starting_score_team1,
            "StartingScoreTeam2": starting_score_team2,
            "StartingGame": None,
            "StartingRound": None,
            "FirstServe": None
        }
        
        if competition_type == "one-to-one":
            competition_data["Team 1 - Player 1 Name"] = player_names[0]
            competition_data["Team 2 - Player 1 Name"] = player_names[1]
        elif competition_type == "two-to-two":
            competition_data["Team 1 - Player 1 Name"] = player_names[0]
            competition_data["Team 1 - Player 2 Name"] = player_names[1]
            competition_data["Team 2 - Player 1 Name"] = player_names[2]
            competition_data["Team 2 - Player 2 Name"] = player_names[3]
        elif competition_type == "one-to-two":
            competition_data["Team 1 - Player 1 Name"] = player_names[0]
            competition_data["Team 2 - Player 1 Name"] = player_names[1]
            competition_data["Team 2 - Player 2 Name"] = player_names[2]
        
        
        new_df = DataFrame([competition_data])
        
        with self.mutex:
            with FileLock("scorers.xlsx.lock"):
                try:
                    existing_df = read_excel("scorers.xlsx")
                    updated_df = concat([existing_df, new_df], ignore_index=True)
                except FileNotFoundError:
                    updated_df = new_df
                
                updated_df.to_excel("scorers.xlsx", index=False)
                    
                self.navigate_to("Referee")