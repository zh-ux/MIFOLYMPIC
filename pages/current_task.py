from flet import *
from pandas import *
import os
import threading
from filelock import FileLock

class CurrentTasks(Container):
    def __init__(self, navigate_to, mutex):
        super().__init__(
            content=Column(
                controls=[
                    ListView(
                        controls=[],
                        expand=True,
                        spacing=20,
                    )
                ],
            ),
            alignment=alignment.center,
            expand=True
        )
        self.name = "Current tasks"
        self.navigate_to = navigate_to
        self.mutex = mutex
        self.timer = None
        self.df = read_excel("scorers.xlsx")
        self.players_name = ["Team 1 - Player 1 Name", "Team 1 - Player 2 Name", "Team 2 - Player 1 Name", "Team 2 - Player 2 Name"]
    
    def reset(self):
        self.content.controls[0].controls.clear()

    def back(self, e):
        self.stop_timer()
        self.navigate_to("Referee")
        
    def update_scores(self):
        with self.mutex:
            with FileLock("Current_tasks.lock"):
                path = "Current_tasks/"
                dir_list = os.listdir(path)
                self.content.controls[0].controls.clear()
                
                if len(dir_list) > 0:
                    for file in dir_list:
                        filename = os.path.splitext(file)[0]
                        with FileLock(path+file+".lock"):
                            if os.path.exists(path+file):
                                df_cf = read_excel(path+file)
                                filtered_df = self.df[self.df['ScorerName'] == filename]
                                task = filtered_df.iloc[0].to_dict()
                                competition_type = task['CompetitionType']
                                
                                score_column = Column(alignment=alignment.center)
                                score_column.controls.append(Text(f"{filename}\n", size=30, color=colors.PRIMARY, weight="bold", text_align=TextAlign.CENTER))
                                
                                names = [task[name] for name in self.players_name]
                                if competition_type == "one-to-one":
                                    score_column.controls.append(Text(f"{names[0]} : {names[2]}\n", size=25, text_align=TextAlign.CENTER))
                                elif competition_type == "two-to-two":
                                    score_column.controls.append(Text(f"{names[0]} {names[1]} : {names[2]} {names[3]}\n", size=25, text_align=TextAlign.CENTER))
                                elif competition_type == "one-to-two":
                                    score_column.controls.append(Text(f"{names[0]} : {names[2]} {names[3]}\n", size=25, text_align=TextAlign.CENTER))
                                        
                                
                                for i in range(1, 4):
                                    scores = df_cf.at[0, f"Game {i} Scores"]
                                    if not isna(scores):
                                        score_column.controls.append(Text(f"Game {i} Scores: {scores}", size=20, text_align=TextAlign.CENTER))
                                    else:
                                        break
                                
                                task_container = Container(
                                    content=score_column,
                                    alignment=alignment.center,
                                    width=300,
                                    border_radius=20,
                                    bgcolor=colors.PRIMARY_CONTAINER
                                )
                                
                                self.content.controls[0].controls.append(task_container)
                        
                self.content.controls[0].controls.append(ElevatedButton(text="Back", on_click=self.back, width=300))
                self.page.update()
    
    def start_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(1, self.refresh)
        self.timer.start()
        
    def refresh(self):
        self.update_scores()
        self.start_timer()
    
    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = False