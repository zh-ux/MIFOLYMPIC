from flet import *
from pandas import *
import os
from filelock import FileLock

class PreviousTasks(Container):
    def __init__(self, navigate_to, mutex):
        super().__init__(
            content=Column(
                controls=[
                    ListView(
                        controls=[],
                        expand=True,
                        spacing=20
                    ),
                    ListView(
                        controls=[
                            Column(controls=[], alignment=MainAxisAlignment.CENTER, horizontal_alignment=MainAxisAlignment.CENTER),
                            Row(
                                controls=[
                                    Column(
                                        controls=[
                                            Row(controls=[Text("1 st", size=25, weight="bold")], ),
                                            Row(
                                                controls=[
                                                    Column(controls=[]),
                                                    Column(controls=[]),
                                                    Column(controls=[])
                                                ],
                                                alignment=MainAxisAlignment.SPACE_EVENLY
                                            )
                                        ],
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=MainAxisAlignment.CENTER
                                    ),
                                    Column(
                                        controls=[
                                            Row(controls=[Text("2 nd", size=25, weight="bold")], alignment=MainAxisAlignment.CENTER),
                                            Row(
                                                controls=[
                                                    Column(controls=[]),
                                                    Column(controls=[]),
                                                    Column(controls=[])
                                                ],
                                                alignment=MainAxisAlignment.SPACE_EVENLY
                                            )
                                        ],
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=MainAxisAlignment.CENTER
                                    ),
                                    Column(
                                        controls=[
                                            Row(controls=[Text("3 rd", size=25, weight="bold")], alignment=MainAxisAlignment.CENTER),
                                            Row(
                                                controls=[
                                                    Column(controls=[]),
                                                    Column(controls=[]),
                                                    Column(controls=[])
                                                ],
                                                alignment=MainAxisAlignment.SPACE_AROUND
                                            )
                                        ],
                                        alignment=MainAxisAlignment.CENTER,
                                        horizontal_alignment=MainAxisAlignment.CENTER
                                    )
                                ],
                                alignment=MainAxisAlignment.SPACE_EVENLY,
                                vertical_alignment=CrossAxisAlignment.START
                            ),
                            ElevatedButton(text="Back", on_click=self.back_previous, width=300)
                        ],
                        expand=True
                    )
                ],
                alignment=alignment.center,
                spacing=20
            ),
            alignment=alignment.center,
            expand=True
        )
        self.name = "Previous tasks"
        self.navigate_to = navigate_to
        self.mutex = mutex
        self.df = read_excel("scorers.xlsx")
        self.players_name = ["Team 1 - Player 1 Name", "Team 1 - Player 2 Name", "Team 2 - Player 1 Name", "Team 2 - Player 2 Name"]
    
    def reset(self):
        self.content.controls[0].controls.clear()
        self.content.controls[1].controls[0].controls.clear()
        for i in range(3):
            self.content.controls[1].controls[1].controls[i].controls[1].controls[0].controls.clear()
            self.content.controls[1].controls[1].controls[i].controls[1].controls[0].controls.append(Text("Round", size=15))
            self.content.controls[1].controls[1].controls[i].controls[1].controls[1].controls.clear()
            self.content.controls[1].controls[1].controls[i].controls[1].controls[1].controls.append(Text("Team 1", size=15))
            self.content.controls[1].controls[1].controls[i].controls[1].controls[2].controls.clear()
            self.content.controls[1].controls[1].controls[i].controls[1].controls[2].controls.append(Text("Team 2", size=15))
        self.content.controls[0].visible = True
        self.content.controls[1].visible = False
        
        with self.mutex:
            with FileLock("Previous_tasks.lock"):
                path = "Previous_tasks"
                dir_list = os.listdir(path) 
                if len(dir_list) > 0:
                    for file in dir_list:
                        filename = os.path.splitext(file)[0]
                        self.content.controls[0].controls.append(ElevatedButton(str(filename), on_click=lambda e, file=filename: self.match_details(file)))
                    self.content.controls[0].controls.append(Container(height=200))
                self.content.controls[0].controls.append(ElevatedButton(text="Back", on_click=self.back_referee, width=300))       

    
    def match_details(self, filename):
        self.content.controls[0].visible = False
        self.content.controls[1].visible = True
        
        with self.mutex:
            with FileLock(f"Previous_tasks\{filename}.xlsx.lock"):
                df_pt = read_excel(f"Previous_tasks\{filename}.xlsx")
                filtered_df = self.df[self.df['ScorerName'] == filename]
                task = filtered_df.iloc[0].to_dict()
                competition_type = task['CompetitionType']
                
                self.content.controls[1].controls[0].controls.append(Text(f"Scorer's Name: {task['ScorerName']}\n", size=20, text_align=TextAlign.CENTER))
                self.content.controls[1].controls[0].controls.append(Text(f"Competition Type: {competition_type}\n", size=20, text_align=TextAlign.CENTER))

                names = [task[name] for name in self.players_name]
                if competition_type == "one-to-one":
                    self.content.controls[1].controls[0].controls.append(Text(f"{names[0]} : {names[2]}\n", size=20, text_align=TextAlign.CENTER))
                elif competition_type == "two-to-two":
                    self.content.controls[1].controls[0].controls.append(Text(f"{names[0]} {names[1]} : {names[2]} {names[3]}\n", size=20, text_align=TextAlign.CENTER))
                elif competition_type == "one-to-two":
                    self.content.controls[1].controls[0].controls.append(Text(f"{names[0]} : {names[2]} {names[3]}\n", size=20, text_align=TextAlign.CENTER))
                
                self.content.controls[1].controls[0].controls.append(Text(f"Match Start Time: {task['MatchStartTime']}\n", size=20, text_align=TextAlign.CENTER))
                
                for i in range(3):
                    for value in df_pt[f"Game {i+1} Round"]:
                        if not isna(value):
                            self.content.controls[1].controls[1].controls[i].controls[1].controls[0].controls.append(Text(str(int(value)), size=15))
                        else:
                            break
                    for value in df_pt[f"Game {i+1} Team 1"]:
                        if not isna(value):
                            self.content.controls[1].controls[1].controls[i].controls[1].controls[1].controls.append(Text(str(int(value)), size=15))
                        else:
                            break
                    for value in df_pt[f"Game {i+1} Team 2"]:
                        if not isna(value):
                            self.content.controls[1].controls[1].controls[i].controls[1].controls[2].controls.append(Text(str(int(value)), size=15))
                        else:
                            break
                self.page.update()
        
    def back_referee(self, e):
        self.navigate_to("Referee")
    
    def back_previous(self, e):
        self.reset()
        self.page.update()