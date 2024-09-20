from flet import *
from pandas import *

class RefereePage(Container):
    def __init__(self, navigate_to):
        super().__init__(
            content=Column(
                controls=[
                    ElevatedButton(text="All tasks", on_click=self.all_tasks, width=200),
                    ElevatedButton(text="Previous tasks", on_click=self.previous_tasks, width=200),
                    ElevatedButton(text="Current tasks", on_click=self.current_tasks, width=200),
                    ElevatedButton(text="Create task", on_click=self.create_task, width=200),
                    ElevatedButton(text="Exit", on_click=self.exit, width=300)
                ],
                alignment=MainAxisAlignment.SPACE_EVENLY,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=20
            ),
            alignment=alignment.center,
            expand=True
        )
        self.name = "Referee"
        self.navigate_to = navigate_to
    
    def all_tasks(self, e):
        self.navigate_to("All tasks")
    
    def previous_tasks(self, e):
        self.navigate_to("Previous tasks")
    
    def current_tasks(self, e):
        self.navigate_to("Current tasks",start_timer=True)
    
    def create_task(self, e):
        self.navigate_to("Create task")
    
    def reset(self):
        pass
    
    def exit(self, e):
        self.navigate_to("First")