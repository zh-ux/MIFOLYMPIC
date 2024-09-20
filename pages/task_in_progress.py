from flet import *
from pandas import *
import time
import threading
import os
import shutil
from filelock import FileLock

class TaskInProgress(Container):
    def __init__(self, navigate_to, mutex):
        super().__init__(
            content=Column(
                controls=[
                    ListView(
                        controls=[
                            Column(
                                controls=[
                                    Stack(
                                        controls=[
                                            Image(src="badminton_court.jpg"),
                                            Container(
                                                content=Text(size=20, weight="bold", color=colors.BLACK)
                                            ),
                                            Container(
                                                content=Text(size=20, weight="bold", color=colors.BLACK)
                                            ),
                                            Container(
                                                content=Text(size=20, weight="bold", color=colors.BLACK)
                                            ),
                                            Container(
                                                content=Text(size=20, weight="bold", color=colors.BLACK)
                                            )
                                        ]
                                        ),
                                    Column(
                                        controls=[
                                            Row(
                                                controls=[
                                                    IconButton(icon=icons.SWAP_VERT_CIRCLE, on_click=self.left_team_swap, icon_size=50),
                                                    IconButton(icon=icons.SWAP_VERT_CIRCLE, on_click=self.right_team_swap, icon_size=50)
                                                ],
                                                alignment=MainAxisAlignment.SPACE_AROUND
                                                ),
                                            Row(
                                                controls=[
                                                    IconButton(icon=icons.CHANGE_CIRCLE, on_click=self.color_swap, icon_size=50),
                                                    IconButton(icon=icons.SWAP_HORIZONTAL_CIRCLE, on_click=self.change_side, icon_size=50)
                                                ],
                                                alignment=MainAxisAlignment.SPACE_EVENLY
                                                ),
                                            Row(controls=[Text(size=20)], alignment=MainAxisAlignment.CENTER),  
                                            Row(controls=[Text(size=20)], alignment=MainAxisAlignment.CENTER),  
                                            Row(controls=[Text(size=20)], alignment=MainAxisAlignment.CENTER),  
                                            Row(
                                                controls=[
                                                    Text(size=20),
                                                    Text(size=20, ref=Ref()),  
                                                ],
                                                alignment=MainAxisAlignment.CENTER
                                            ),
                                            Row(
                                                controls=[
                                                    Text(size=20),
                                                    Text(size=20, ref=Ref())
                                                ],
                                                alignment=MainAxisAlignment.CENTER
                                                ),
                                            Row(
                                                controls=[
                                                    ElevatedButton(text="Team 1 Score", on_click=self.team1_score),
                                                    ElevatedButton(text="Team 2 Score", on_click=self.team2_score)
                                                ],
                                                alignment=MainAxisAlignment.CENTER
                                            ),
                                            Row(controls=[Text("Round: 0", size=20, ref=Ref())], alignment=MainAxisAlignment.CENTER),
                                            Row(
                                                controls=[
                                                    IconButton(icon=icons.TIMER, on_click=self.start_timer, icon_size=50),
                                                    IconButton(icon=icons.TIMER_OFF, on_click=self.reset_timer, icon_size=50),
                                                    IconButton(icon=icons.UNDO_ROUNDED, on_click=self.undo, icon_size=50)
                                                ],
                                                alignment=MainAxisAlignment.SPACE_EVENLY
                                            ),
                                            Row(controls=[Text("Time: 00:00", size=20, ref=Ref())], alignment=MainAxisAlignment.CENTER)
                                        ],
                                        spacing=20
                                    ),
                                    Row(controls=[ElevatedButton(text="Done", on_click=self.done, width=300)], alignment=MainAxisAlignment.CENTER),
                                    Row(controls=[ElevatedButton(text="Exit", on_click=self.exit, width=300)], alignment=MainAxisAlignment.CENTER)
                                ],
                                alignment=MainAxisAlignment.SPACE_AROUND
                            ),
                        ],
                        expand=True,
                        spacing=20
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=alignment.center,
            expand=True
        )
        
        self.name = "Task in progress"
        self.navigate_to = navigate_to
        self.mutex = mutex
        self.width = None
        self.height = None
        self.username = None
        self.file_path = None
        self.single_player = None
        self.first_position = [["", "", "", ""], [None, None, None, None]]
        self.competition_type = None
        self.middle_rest = None
        self.left_team = None
        self.right_team = None
        self.match_data = [[],[]]
        self.scores = {"Team 1": 0, "Team 2": 0}
        self.games = {"Team 1": 0, "Team 2": 0}
        self.timer_start_time = None
        self.start_round = 0
        self.current_round = 0
        self.current_game = 0
        self.server = None
        self.timer_interval = None
    
    def load_tasks(self, username):
        with self.mutex:
            self.username = username
            self.file_path = f"Current_tasks\{username}.xlsx"
            with FileLock("scorers.xlsx.lock"):
                df = read_excel("scorers.xlsx")
                filtered_df = df[df['ScorerName'] == username]
                task = filtered_df.iloc[0].to_dict()
                self.competition_type = str(task["CompetitionType"])
                self.left_team = "team1"
                self.right_team = "team2"
                self.content.controls[0].controls[0].controls[1].controls[2].controls[0].value = f"Scorer's Name: {task['ScorerName']}"
                self.content.controls[0].controls[0].controls[1].controls[3].controls[0].value = f"Competition Type: {task['CompetitionType']}"
                self.content.controls[0].controls[0].controls[1].controls[4].controls[0].value = f"Match Start Time: {task['MatchStartTime']}"
                
                players_name = ["Team 1 - Player 1 Name", "Team 1 - Player 2 Name", "Team 2 - Player 1 Name", "Team 2 - Player 2 Name"]
                team1_names = []
                team2_names = []
                if self.competition_type == "one-to-two":
                    self.single_player = f"{task["Team 1 - Player 1 Name"]}"
                for idx, name in enumerate(players_name, 1):
                    self.content.controls[0].controls[0].controls[0].controls[idx].content.value = ""
                    if not isna(task[name]):
                        self.content.controls[0].controls[0].controls[0].controls[idx].content.value = f"{task[name]}"
                        if idx == 1 or idx == 2:
                            team1_names.append(f"({task[name]})")
                        elif idx == 3 or idx == 4:
                            team2_names.append(f"({task[name]})")

                self.content.controls[0].controls[0].controls[1].controls[5].controls[0].value = f"Score Team 1 [{ ' '.join(team1_names) }] : "
                self.content.controls[0].controls[0].controls[1].controls[6].controls[0].value = f"Score Team 2 [{ ' '.join(team2_names) }] : "
                
                self.scores = {"Team 1": int(task['StartingScoreTeam1']), "Team 2": int(task['StartingScoreTeam2'])}
                self.content.controls[0].controls[0].controls[1].controls[5].controls[1].value = str(self.scores["Team 1"])
                self.content.controls[0].controls[0].controls[1].controls[6].controls[1].value = str(self.scores["Team 2"])
                if self.scores["Team 1"] >= 11 or self.scores["Team 2"] >= 11:
                    self.middle_rest = True
                self.color()
                self.image()
                if not isna(task['FirstServe']):
                    self.server = int(task['FirstServe'])
                    if self.server == 1 or self.server == 2:
                        self.content.controls[0].controls[0].controls[0].controls[3].content.color = colors.BLACK
                        self.content.controls[0].controls[0].controls[0].controls[4].content.color = colors.BLACK
                    elif self.server == 3 or self.server == 4:
                        self.content.controls[0].controls[0].controls[0].controls[1].content.color = colors.BLACK
                        self.content.controls[0].controls[0].controls[0].controls[2].content.color = colors.BLACK
                else:
                    self.content.controls[0].controls[0].controls[0].controls[3].content.color = colors.BLACK
                    self.content.controls[0].controls[0].controls[0].controls[4].content.color = colors.BLACK
                if not isna(task['StartingGame']):
                    self.current_game = int(task['StartingGame'])
                if not isna(task['StartingRound']):
                    self.start_round = int(task['StartingRound'])
                    self.current_round = int(task['StartingRound'])
                self.content.controls[0].controls[0].controls[1].controls[8].controls[0].value = f"Round: {self.current_round}"
                self.check_server()
                self.page.update()

    def done(self, dialog):
        reminder_dialog = AlertDialog(
            modal=True,
            title=Text("Reminder"),
            content=Text("Do you sure you have done the task already?"),
            actions=[
                TextButton("Yes", on_click=lambda e: self.move_file(reminder_dialog)),
                TextButton("No", on_click=lambda e: self.close_dialog(reminder_dialog))
            ],
            open=True
        )
        self.page.dialog = reminder_dialog
        self.page.update()
    
    def exit(self, e):
        reminder_dialog = AlertDialog(
            modal=True,
            title=Text("Reminder"),
            content=Text("Do you sure you want to exit?"),
            actions=[
                TextButton("Yes", on_click=lambda e: self.confirm_exit(reminder_dialog)),
                TextButton("No", on_click=lambda e: self.close_dialog(reminder_dialog))
            ],
            open=True
        )
        self.page.dialog = reminder_dialog
        self.page.update()

    def confirm_exit(self, dialog):
        with self.mutex:
            with FileLock("scorers.xlsx.lock"):
                df = read_excel("scorers.xlsx")
                df.loc[df["ScorerName"] == self.username, "StartingScoreTeam1"] = self.scores["Team 1"]
                df.loc[df["ScorerName"] == self.username, "StartingScoreTeam2"] = self.scores["Team 2"]
                df.loc[df["ScorerName"] == self.username, "StartingGame"] = self.current_game
                df.loc[df["ScorerName"] == self.username, "StartingRound"] = self.current_round
                df.loc[df["ScorerName"] == self.username, "FirstServe"] = self.server
                df.to_excel("scorers.xlsx", index=False)
                self.close_dialog(dialog)
                self.navigate_to("First")
    
    def handle_disconnect(self, e):
        with self.mutex:
            if self.visible:
                with FileLock("scorers.xlsx.lock"):
                    df = read_excel("scorers.xlsx")
                    df.loc[df["ScorerName"] == self.username, "StartingScoreTeam1"] = self.scores["Team 1"]
                    df.loc[df["ScorerName"] == self.username, "StartingScoreTeam2"] = self.scores["Team 2"]
                    df.loc[df["ScorerName"] == self.username, "StartingGame"] = self.current_game
                    df.loc[df["ScorerName"] == self.username, "StartingRound"] = self.current_round
                    df.loc[df["ScorerName"] == self.username, "FirstServe"] = self.server
                    df.to_excel("scorers.xlsx", index=False)
    
    def handle_close(self, e):
        with self.mutex:
            if self.visible:
                with FileLock("scorers.xlsx.lock"):
                    df = read_excel("scorers.xlsx")
                    df.loc[df["ScorerName"] == self.username, "StartingScoreTeam1"] = self.scores["Team 1"]
                    df.loc[df["ScorerName"] == self.username, "StartingScoreTeam2"] = self.scores["Team 2"]
                    df.loc[df["ScorerName"] == self.username, "StartingGame"] = self.current_game
                    df.loc[df["ScorerName"] == self.username, "StartingRound"] = self.current_round
                    df.loc[df["ScorerName"] == self.username, "FirstServe"] = self.server
                    df.to_excel("scorers.xlsx", index=False)
        
    def init_page(self, page: Page):
        self.page = page
        self.page.on_disconnect = self.handle_disconnect
        self.page.on_close = self.handle_close

    def position(self, page: Page):
        self.width = page.width
        self.height = page.height

    def image(self):
        self.content.controls[0].controls[0].controls[0].controls[0].width = self.width
        self.content.controls[0].controls[0].controls[0].controls[1].left = self.width*0.2
        self.content.controls[0].controls[0].controls[0].controls[2].left = self.width*0.2
        self.content.controls[0].controls[0].controls[0].controls[3].right = self.width*0.2
        self.content.controls[0].controls[0].controls[0].controls[4].right = self.width*0.2
        self.content.controls[0].controls[0].controls[0].controls[1].top = self.width*0.1
        self.content.controls[0].controls[0].controls[0].controls[2].bottom = self.width*0.1
        self.content.controls[0].controls[0].controls[0].controls[3].top = self.width*0.1
        self.content.controls[0].controls[0].controls[0].controls[4].bottom = self.width*0.1

    def reset(self):
        self.left_team = "team1"
        self.right_team = "team2"
        self.match_data = [[],[]]
        self.scores = {"Team 1": 0, "Team 2": 0}
        self.middle_rest = False
        self.timer_start_time = None
        self.current_round = 0
        self.current_game = 0

        self.content.controls[0].controls[0].controls[1].controls[8].controls[0].value = "Round: 0"
        if self.content.controls[0].controls[0].controls[1].controls[7].controls[0].text != "Team 1 Score":
            self.content.controls[0].controls[0].controls[1].controls[7].controls[0], self.content.controls[0].controls[0].controls[1].controls[7].controls[1] = self.content.controls[0].controls[0].controls[1].controls[7].controls[1], self.content.controls[0].controls[0].controls[1].controls[7].controls[0]
    
    def left_team_swap(self, e):
        self.content.controls[0].controls[0].controls[0].controls[1].content.value, self.content.controls[0].controls[0].controls[0].controls[2].content.value = self.content.controls[0].controls[0].controls[0].controls[2].content.value, self.content.controls[0].controls[0].controls[0].controls[1].content.value
        self.page.update()
    
    def right_team_swap(self, e):
        self.content.controls[0].controls[0].controls[0].controls[3].content.value, self.content.controls[0].controls[0].controls[0].controls[4].content.value = self.content.controls[0].controls[0].controls[0].controls[4].content.value, self.content.controls[0].controls[0].controls[0].controls[3].content.value
        self.page.update()
    
    def change_side(self, e):
        self.content.controls[0].controls[0].controls[0].controls[1].content.value, self.content.controls[0].controls[0].controls[0].controls[4].content.value = self.content.controls[0].controls[0].controls[0].controls[4].content.value, self.content.controls[0].controls[0].controls[0].controls[1].content.value
        self.content.controls[0].controls[0].controls[0].controls[2].content.value, self.content.controls[0].controls[0].controls[0].controls[3].content.value = self.content.controls[0].controls[0].controls[0].controls[3].content.value, self.content.controls[0].controls[0].controls[0].controls[2].content.value
        self.content.controls[0].controls[0].controls[0].controls[1].content.color, self.content.controls[0].controls[0].controls[0].controls[4].content.color = self.content.controls[0].controls[0].controls[0].controls[4].content.color, self.content.controls[0].controls[0].controls[0].controls[1].content.color
        self.content.controls[0].controls[0].controls[0].controls[2].content.color, self.content.controls[0].controls[0].controls[0].controls[3].content.color = self.content.controls[0].controls[0].controls[0].controls[3].content.color, self.content.controls[0].controls[0].controls[0].controls[2].content.color
        self.content.controls[0].controls[0].controls[1].controls[7].controls[0], self.content.controls[0].controls[0].controls[1].controls[7].controls[1] = self.content.controls[0].controls[0].controls[1].controls[7].controls[1], self.content.controls[0].controls[0].controls[1].controls[7].controls[0]
        self.left_team, self.right_team = self.right_team, self.left_team
        self.check_server()
        self.page.update()
        
    def color(self):
        if self.left_team == "team1" and self.right_team == "team2":
            if self.scores["Team 1"] % 2 == 0:
                self.content.controls[0].controls[0].controls[0].controls[2].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[1].content.color = colors.BLACK
            elif self.scores["Team 1"] % 2 == 1:
                self.content.controls[0].controls[0].controls[0].controls[1].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[2].content.color = colors.BLACK
            if self.scores["Team 2"] % 2 == 0:
                self.content.controls[0].controls[0].controls[0].controls[3].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[4].content.color = colors.BLACK
            elif self.scores["Team 2"] % 2 == 1:
                self.content.controls[0].controls[0].controls[0].controls[4].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[3].content.color = colors.BLACK
        elif self.left_team == "team2" and self.right_team == "team1":
            if self.scores["Team 1"] % 2 == 0:
                self.content.controls[0].controls[0].controls[0].controls[3].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[4].content.color = colors.BLACK
            elif self.scores["Team 1"] % 2 == 1:
                self.content.controls[0].controls[0].controls[0].controls[4].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[3].content.color = colors.BLACK
            if self.scores["Team 2"] % 2 == 0:
                self.content.controls[0].controls[0].controls[0].controls[2].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[1].content.color = colors.BLACK
            elif self.scores["Team 2"] % 2 == 1:
                self.content.controls[0].controls[0].controls[0].controls[1].content.color = colors.RED
                self.content.controls[0].controls[0].controls[0].controls[2].content.color = colors.BLACK
        
    def color_swap(self, e):
        if self.content.controls[0].controls[0].controls[0].controls[1].content.color == colors.RED or self.content.controls[0].controls[0].controls[0].controls[2].content.color == colors.RED:
            self.color()
            self.content.controls[0].controls[0].controls[0].controls[1].content.color = colors.BLACK
            self.content.controls[0].controls[0].controls[0].controls[2].content.color = colors.BLACK
        elif self.content.controls[0].controls[0].controls[0].controls[3].content.color == colors.RED or self.content.controls[0].controls[0].controls[0].controls[4].content.color == colors.RED:
            self.color()
            self.content.controls[0].controls[0].controls[0].controls[3].content.color = colors.BLACK
            self.content.controls[0].controls[0].controls[0].controls[4].content.color = colors.BLACK
        self.check_server()
        self.page.update()
    
    def check_server(self):
        for i in range(1, 5):
            if self.content.controls[0].controls[0].controls[0].controls[i].content.color == colors.RED:
                self.server = i
    
    def change_server(self):
        if self.competition_type == "one-to-one":
            if self.left_team == "team1" and self.right_team == "team2":
                
                if self.match_data[0][-1] == 1 and self.server in (1, 2):
                    self.content.controls[0].controls[0].controls[0].controls[1].content.color, self.content.controls[0].controls[0].controls[0].controls[2].content.color = self.content.controls[0].controls[0].controls[0].controls[2].content.color, self.content.controls[0].controls[0].controls[0].controls[1].content.color
                elif self.match_data[1][-1] == 1 and self.server in (1, 2):
                    self.color_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (3, 4):
                    self.content.controls[0].controls[0].controls[0].controls[3].content.color, self.content.controls[0].controls[0].controls[0].controls[4].content.color = self.content.controls[0].controls[0].controls[0].controls[4].content.color, self.content.controls[0].controls[0].controls[0].controls[3].content.color
                elif self.match_data[0][-1] == 1 and self.server in (3, 4):
                    self.color_swap(e=None)
                self.check_server()
                if self.server == 1 and self.content.controls[0].controls[0].controls[0].controls[1].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                elif self.server == 2 and self.content.controls[0].controls[0].controls[0].controls[2].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                elif self.server == 3 and self.content.controls[0].controls[0].controls[0].controls[3].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                elif self.server == 4 and self.content.controls[0].controls[0].controls[0].controls[4].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                        
            elif self.left_team == "team2" and self.right_team == "team1":
                
                if self.match_data[0][-1] == 1 and self.server in (3, 4):
                    self.content.controls[0].controls[0].controls[0].controls[3].content.color, self.content.controls[0].controls[0].controls[0].controls[4].content.color = self.content.controls[0].controls[0].controls[0].controls[4].content.color, self.content.controls[0].controls[0].controls[0].controls[3].content.color
                elif self.match_data[1][-1] == 1 and self.server in (3, 4):
                    self.color_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (1, 2):
                    self.content.controls[0].controls[0].controls[0].controls[1].content.color, self.content.controls[0].controls[0].controls[0].controls[2].content.color = self.content.controls[0].controls[0].controls[0].controls[2].content.color, self.content.controls[0].controls[0].controls[0].controls[1].content.color
                elif self.match_data[0][-1] == 1 and self.server in (1, 2):
                    self.color_swap(e=None)
                    
                self.check_server()
                if self.server == 1 and self.content.controls[0].controls[0].controls[0].controls[1].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                elif self.server == 2 and self.content.controls[0].controls[0].controls[0].controls[2].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                elif self.server == 3 and self.content.controls[0].controls[0].controls[0].controls[3].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                elif self.server == 4 and self.content.controls[0].controls[0].controls[0].controls[4].content.value == "":
                    self.left_team_swap(e=None)
                    self.right_team_swap(e=None)
                    
        elif self.competition_type == "two-to-two":
            if self.left_team == "team1" and self.right_team == "team2":
                if self.match_data[0][-1] == 1 and self.server in (1, 2):
                    self.content.controls[0].controls[0].controls[0].controls[1].content.color, self.content.controls[0].controls[0].controls[0].controls[2].content.color = self.content.controls[0].controls[0].controls[0].controls[2].content.color, self.content.controls[0].controls[0].controls[0].controls[1].content.color
                    self.left_team_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (1, 2):
                    self.color_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (3, 4):
                    self.content.controls[0].controls[0].controls[0].controls[3].content.color, self.content.controls[0].controls[0].controls[0].controls[4].content.color = self.content.controls[0].controls[0].controls[0].controls[4].content.color, self.content.controls[0].controls[0].controls[0].controls[3].content.color
                    self.right_team_swap(e=None)
                elif self.match_data[0][-1] == 1 and self.server in (3, 4):
                    self.color_swap(e=None)
            elif self.left_team == "team2" and self.right_team == "team1":
                if self.match_data[0][-1] == 1 and self.server in (3, 4):
                    self.content.controls[0].controls[0].controls[0].controls[3].content.color, self.content.controls[0].controls[0].controls[0].controls[4].content.color = self.content.controls[0].controls[0].controls[0].controls[4].content.color, self.content.controls[0].controls[0].controls[0].controls[3].content.color
                    self.right_team_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (3, 4):
                    self.color_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (1, 2):
                    self.content.controls[0].controls[0].controls[0].controls[1].content.color, self.content.controls[0].controls[0].controls[0].controls[2].content.color = self.content.controls[0].controls[0].controls[0].controls[2].content.color, self.content.controls[0].controls[0].controls[0].controls[1].content.color
                    self.left_team_swap(e=None)
                elif self.match_data[0][-1] == 1 and self.server in (1, 2):
                    self.color_swap(e=None)
            self.check_server()
        elif self.competition_type == "one-to-two":
            if self.left_team == "team1":
                if self.match_data[0][-1] == 1 and self.server in (1, 2):
                    self.content.controls[0].controls[0].controls[0].controls[1].content.color, self.content.controls[0].controls[0].controls[0].controls[2].content.color = self.content.controls[0].controls[0].controls[0].controls[2].content.color, self.content.controls[0].controls[0].controls[0].controls[1].content.color
                elif self.match_data[1][-1] == 1 and self.server in (1, 2):
                    self.color_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (3, 4):
                    self.content.controls[0].controls[0].controls[0].controls[3].content.color, self.content.controls[0].controls[0].controls[0].controls[4].content.color = self.content.controls[0].controls[0].controls[0].controls[4].content.color, self.content.controls[0].controls[0].controls[0].controls[3].content.color
                    self.right_team_swap(e=None)
                elif self.match_data[0][-1] == 1 and self.server in (3, 4):
                    self.color_swap(e=None)
                self.check_server()
                if self.server == 1 and self.content.controls[0].controls[0].controls[0].controls[2].content.value == self.single_player:
                    self.left_team_swap(e=None)
                elif self.server == 2 and self.content.controls[0].controls[0].controls[0].controls[1].content.value == self.single_player:
                    self.left_team_swap(e=None)
                elif self.server == 3 and self.content.controls[0].controls[0].controls[0].controls[1].content.value == self.single_player:
                    self.left_team_swap(e=None)
                elif self.server == 4 and self.content.controls[0].controls[0].controls[0].controls[2].content.value == self.single_player:
                    self.left_team_swap(e=None)
                    
            elif self.right_team == "team1":   
                if self.match_data[0][-1] == 1 and self.server in (1, 2):
                    self.color_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (1, 2):
                    self.content.controls[0].controls[0].controls[0].controls[1].content.color, self.content.controls[0].controls[0].controls[0].controls[2].content.color = self.content.controls[0].controls[0].controls[0].controls[2].content.color, self.content.controls[0].controls[0].controls[0].controls[1].content.color
                    self.left_team_swap(e=None)
                elif self.match_data[1][-1] == 1 and self.server in (3, 4):
                    self.color_swap(e=None)
                elif self.match_data[0][-1] == 1 and self.server in (3, 4):
                    self.content.controls[0].controls[0].controls[0].controls[3].content.color, self.content.controls[0].controls[0].controls[0].controls[4].content.color = self.content.controls[0].controls[0].controls[0].controls[4].content.color, self.content.controls[0].controls[0].controls[0].controls[3].content.color
                self.right_team_swap(e=None)
                self.check_server()
                if self.server == 1 and self.content.controls[0].controls[0].controls[0].controls[3].content.value == self.single_player:
                    self.right_team_swap(e=None)
                elif self.server == 2 and self.content.controls[0].controls[0].controls[0].controls[4].content.value == self.single_player:
                    self.right_team_swap(e=None)
                elif self.server == 3 and self.content.controls[0].controls[0].controls[0].controls[4].content.value == self.single_player:
                    self.right_team_swap(e=None)
                elif self.server == 4 and self.content.controls[0].controls[0].controls[0].controls[3].content.value == self.single_player:
                    self.right_team_swap(e=None)
            
    def team1_score(self, e):
        with self.mutex:
            if self.current_round == self.start_round:
                for i in range(1, 5):
                    self.first_position[0][i-1] = self.content.controls[0].controls[0].controls[0].controls[i].content.value
                    self.first_position[1][i-1] = self.content.controls[0].controls[0].controls[0].controls[i].content.color
            self.scores["Team 1"] += 1
            self.match_data[0].append(1)
            self.match_data[1].append(0)
            self.content.controls[0].controls[0].controls[1].controls[5].controls[1].value = str(self.scores["Team 1"])
            self.current_round += 1
            self.content.controls[0].controls[0].controls[1].controls[8].controls[0].value = f"Round: {self.current_round}"
            self.change_server()
            self.update_score()
            self.check_score()
            self.page.update()

    def team2_score(self, e):
        with self.mutex:
            if self.current_round == self.start_round:
                for i in range(1, 5):
                    self.first_position[0][i-1] = self.content.controls[0].controls[0].controls[0].controls[i].content.value
                    self.first_position[1][i-1] = self.content.controls[0].controls[0].controls[0].controls[i].content.color
            self.scores["Team 2"] += 1
            self.match_data[1].append(1)
            self.match_data[0].append(0)
            self.content.controls[0].controls[0].controls[1].controls[6].controls[1].value = str(self.scores["Team 2"])
            self.current_round += 1
            self.content.controls[0].controls[0].controls[1].controls[8].controls[0].value = f"Round: {self.current_round}"
            self.change_server()
            self.update_score()
            self.check_score()
            self.page.update()
    
    def update_score(self):
        with FileLock(self.file_path+".lock"):
            if not os.path.exists(self.file_path):
                df = DataFrame(columns=[
                    "Game 1 Round", "Game 1 Team 1", "Game 1 Team 2",
                    "Game 2 Round", "Game 2 Team 1", "Game 2 Team 2",
                    "Game 3 Round", "Game 3 Team 1", "Game 3 Team 2",
                    "Game 1 Scores", "Game 2 Scores", "Game 3 Scores"
                ])
                df.to_excel(self.file_path, index=False)
            
            df = read_excel(self.file_path)
            round_columns = self.get_round_column()
        
        if self.current_round <= len(df):
            df.at[self.current_round - 1, round_columns["Round"]] = self.current_round
            df.at[self.current_round - 1, round_columns["Team 1"]] = self.scores["Team 1"]
            df.at[self.current_round - 1, round_columns["Team 2"]] = self.scores["Team 2"]
        else:
            new_row = {
                round_columns["Round"]: self.current_round,
                round_columns["Team 1"]: self.scores["Team 1"],
                round_columns["Team 2"]: self.scores["Team 2"]
            }
            df = df._append(new_row, ignore_index=True)
        
        df.at[0, round_columns["Scores"]] = f"{self.scores['Team 1']}:{self.scores['Team 2']}"
        
        df.to_excel(self.file_path, index=False)
  
    def get_round_column(self):
        columns = {
        0: {"Round": "Game 1 Round", "Team 1": "Game 1 Team 1", "Team 2": "Game 1 Team 2", "Scores": "Game 1 Scores"},
        1: {"Round": "Game 2 Round", "Team 1": "Game 2 Team 1", "Team 2": "Game 2 Team 2", "Scores": "Game 2 Scores"},
        2: {"Round": "Game 3 Round", "Team 1": "Game 3 Team 1", "Team 2": "Game 3 Team 2", "Scores": "Game 3 Scores"},
        }
        return columns[self.current_game]
        
    def undo(self, dialog=None):
        with self.mutex:
            if self.current_round > self.start_round:
                
                if self.scores["Team 1"] == 21 and self.scores["Team 2"] <= 20:
                    self.games["Team 1"] -= 1
                    self.current_game -= 1
                elif self.scores["Team 2"] == 21 and self.scores["Team 1"] <= 20:
                    self.games["Team 2"] -= 1
                    self.current_game -= 1
                elif 20 <= self.scores["Team 1"] < 30 and 20<= self.scores["Team 2"] < 30 and self.scores["Team 1"] - self.scores["Team 2"] == 2:
                    self.games["Team 1"] -= 1
                    self.current_game -= 1
                elif 20 <= self.scores["Team 1"] < 30 and 20<= self.scores["Team 2"] < 30 and self.scores["Team 2"] - self.scores["Team 1"] == 2:
                    self.games["Team 2"] -= 1
                    self.current_game -= 1
                elif self.scores["Team 1"] == 30:
                    self.games["Team 1"] -= 1
                    self.current_game -= 1
                elif self.scores["Team 2"] == 30:
                    self.games["Team 2"] -= 1
                    self.current_game -= 1
                    
                if self.match_data[0][-1] == 1:
                    self.scores["Team 1"] -= 1
                elif self.match_data[1][-1] == 1:
                    self.scores["Team 2"] -= 1
                
                self.current_round -= 1
                self.content.controls[0].controls[0].controls[1].controls[5].controls[1].value = str(self.scores["Team 1"])
                self.content.controls[0].controls[0].controls[1].controls[6].controls[1].value = str(self.scores["Team 2"])
                self.content.controls[0].controls[0].controls[1].controls[8].controls[0].value = f"Round: {self.current_round}"
                self.match_data[0].pop()
                self.match_data[1].pop()
                
                if (self.scores["Team 1"] == 11 and self.scores["Team 2"] < 11) or (self.scores["Team 2"] == 11 and self.scores["Team 1"] < 11):
                    self.change_side(e=None)
                    self.middle_rest = False

                if self.current_round == self.start_round:
                    for i in range(1, 5):
                        self.content.controls[0].controls[0].controls[0].controls[i].content.value = self.first_position[0][i-1]
                        self.content.controls[0].controls[0].controls[0].controls[i].content.color = self.first_position[1][i-1]
                else:
                    self.change_server()
                
                if dialog:
                    self.close_dialog(dialog)
                
                self.update_score()
                self.page.update()

    def check_score(self):
        if self.scores["Team 1"] == 11 or self.scores["Team 2"] == 11:
            self.show_reminder("A side has reached 11 points!")
            
        if self.scores["Team 1"] == 21 and self.scores["Team 2"] < 20:
            self.games["Team 1"] += 1
            self.current_game += 1
            self.check_game()
        elif self.scores["Team 2"] == 21 and self.scores["Team 1"] < 20:
            self.games["Team 2"] += 1
            self.current_game += 1
            self.check_game()
        elif 20 <= self.scores["Team 1"] < 30 and 20<= self.scores["Team 2"] <30 and self.scores["Team 1"] - self.scores["Team 2"]==2:
            self.games["Team 1"] += 1
            self.current_game += 1
            self.check_game()
        elif 20 <= self.scores["Team 1"] < 30 and 20<= self.scores["Team 2"] <30 and self.scores["Team 2"] - self.scores["Team 1"]==2:
            self.games["Team 2"] += 1
            self.current_game += 1
            self.check_game()
        elif self.scores["Team 1"] == 30:
            self.games["Team 1"] += 1
            self.current_game += 1
            self.check_game()
        elif self.scores["Team 2"] == 30:
            self.games["Team 2"] += 1
            self.current_game += 1
            self.check_game()
        elif self.scores["Team 1"] > 30 or self.scores["Team 2"] > 30:
            self.show_reminder("Error!")

        self.page.update()
    
    def check_game(self):
        if self.games["Team 1"] == 2:
            self.show_reminder("Team 1 Win!")
        elif self.games["Team 2"] == 2:
            self.show_reminder("Team 2 Win!")
        else:
            self.show_reminder("End of this match!")
    
    def move_file(self, dialog):
        source = "Current_tasks"
        destination = "Previous_tasks"
        with FileLock(source+".lock"), FileLock(destination+".lock"):
            src_path = os.path.join(source, f"{self.username}.xlsx")
            dst_path = os.path.join(destination, f"{self.username}.xlsx")
            shutil.move(src_path, dst_path)
            self.close_dialog(dialog)
            self.navigate_to("First")
        
    def next_match(self, dialog):
        self.content.controls[0].controls[0].controls[1].controls[5].controls[1].value = 0
        self.content.controls[0].controls[0].controls[1].controls[6].controls[1].value = 0
        self.content.controls[0].controls[0].controls[1].controls[8].controls[0].value = "Round: 0"
        self.match_data = [[],[]]
        self.scores = {"Team 1": 0, "Team 2": 0}
        self.current_round = 0
        self.middle_rest = False
        self.change_side(e=None)
        self.color_swap(e=None)
        self.color_swap(e=None)
        self.close_dialog(dialog)
        self.page.update()
    
    def middle_rest_reminder(self, dialog): 
        self.change_side(e=None)
        self.middle_rest = True
        self.close_dialog(dialog)

    def show_reminder(self, message):
        if message == "End of this match!":
            reminder_dialog = AlertDialog(
                modal=True,
                title=Text("Reminder"),
                content=Text(message),
                actions=[
                    TextButton("Next Match!", on_click=lambda e: self.next_match(reminder_dialog)),
                    TextButton("Undo", on_click=lambda e: self.undo(dialog=reminder_dialog))
                    ],
                open=True
            )
        elif message == "Team 1 Win!" or message == "Team 2 Win!":
            reminder_dialog = AlertDialog(
                modal=True,
                title=Text("Reminder"),
                content=Text(message),
                actions=[
                    TextButton("Confirm", on_click=lambda e: self.move_file(reminder_dialog)),
                    TextButton("Undo", on_click=lambda e: self.undo(dialog=reminder_dialog))
                ],
                open=True
            )
        elif message == "A side has reached 11 points!" and not self.middle_rest:
            reminder_dialog = AlertDialog(
                modal=True,
                title=Text("Reminder"),
                content=Text(message),
                actions=[TextButton("OK", on_click=lambda e: self.middle_rest_reminder(reminder_dialog))],
                open=True
            )
        elif message == "Error!":
            reminder_dialog = AlertDialog(
                modal=True,
                title=Text("Reminder"),
                content=Text(message),
                actions=[TextButton("OK", on_click=lambda e: self.middle_rest_reminder(reminder_dialog))],
                open=True
            )
        self.page.dialog = reminder_dialog
        self.page.update()

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def start_timer(self, e):
        self.timer_start_time = time.time()
        self.timer_interval = threading.Timer(1, self.update_timer)
        self.timer_interval.start()

    def reset_timer(self, e):
        self.timer_start_time = None
        self.content.controls[0].controls[0].controls[1].controls[10].controls[0].value = "Time: 00:00"
        if self.timer_interval:
            self.timer_interval.cancel()
            self.timer_interval = None
        self.page.update()

    def update_timer(self):
        while self.timer_start_time:
            elapsed_time = int(time.time() - self.timer_start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.content.controls[0].controls[0].controls[1].controls[10].controls[0].value = f"Time: {minutes:02}:{seconds:02}"
            self.page.update()
            time.sleep(1)