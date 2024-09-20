from flet import *
from pandas import *
from filelock import FileLock


class ScorerPage(Container):
    def __init__(self, navigate_to, mutex):
        super().__init__(
            content=Column(
                controls=[
                    Text(value="", size=20),
                    Text(value="", size=20),
                    Column(
                        controls=[],
                        alignment=MainAxisAlignment.SPACE_EVENLY
                        ),
                    Text(size=20),
                    Column(
                        controls=[
                            Text(value="", size=20),
                            Text(value="", size=20)
                        ],
                        alignment=MainAxisAlignment.SPACE_EVENLY,
                    ),
                    ElevatedButton(
                        text="Continue",
                        on_click=self.continue_task,
                        width=300
                    )
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=alignment.center,
            expand=True
        )
        self.name = "Scorer"
        self.navigate_to = navigate_to
        self.mutex = mutex
        self.player_names_column = self.content.controls[2]
        self.username = None  
    
    def load_tasks(self, username):
        self.username = username
        with self.mutex:
            with FileLock("scorers.xlsx.lock"):
                try:
                    df = read_excel("scorers.xlsx")
                    if not df.empty:
                        filtered_df = df[df['ScorerName'] == username]
                        task = filtered_df.iloc[0].to_dict()
                        self.content.controls[0].value = f"Scorer's Name: {task['ScorerName']}"
                        self.content.controls[1].value = f"Competition Type: {task['CompetitionType']}"
                        self.content.controls[3].value = f"Match Start Time: {task['MatchStartTime']}"
                        self.content.controls[4].controls[0].value = f"Starting Score Team 1: {task['StartingScoreTeam1']}"
                        self.content.controls[4].controls[1].value = f"Starting Score Team 2: {task['StartingScoreTeam2']}"
                        
                        player_names = ["Team 1 - Player 1 Name", "Team 1 - Player 2 Name", "Team 2 - Player 1 Name", "Team 2 - Player 2 Name"]
                        for name in player_names:
                            if not isna(task[name]):
                                self.content.controls[2].controls.append(Text(f"{name}: {task[name]}", size=20))
                        
                    else:
                        print("No tasks available.")
                except FileNotFoundError:
                    print("scorers.xlsx not found.")
                
                self.page.update()
    
    def reset(self):
        self.content.controls[2].controls.clear()
        
    def continue_task(self, e):
        self.navigate_to("Task in progress", self.username)