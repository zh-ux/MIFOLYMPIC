from flet import *
from pandas import *
from filelock import FileLock

class FirstPage(Container):
    def __init__(self, navigate_to, mutex):
        super().__init__(
            content=Column(
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    TextField(label="Enter Username", width=300),
                    ElevatedButton(
                        text="Submit",
                        on_click=self.submit,
                        width=100
                    )
                ]
            ),
            alignment=alignment.center,
            expand=True
        )
        self.name = "First"
        self.navigate_to = navigate_to
        self.mutex = mutex
    
    def reset(self):
        self.content.controls[0].value = ""
        
    def submit(self, e):
        username = self.content.controls[0].value
        if self.is_referee(username):
            self.navigate_to("Referee")
        elif self.is_scorer(username):
            self.navigate_to("Scorer", username)
        else:
            self.show_error_dialog("Username not found! Please try again.")

    def is_referee(self, username):
        referees_df = read_excel('referees.xlsx')
        return username in referees_df['RefereeName'].values

    def is_scorer(self, username):
        scorers_df = read_excel('scorers.xlsx')
        return username in scorers_df['ScorerName'].values

    def show_error_dialog(self, message):
        dialog = AlertDialog(
            title=Text("Error"),
            content=Text(message),
            actions=[
                TextButton("OK", on_click=lambda e: self.close_dialog(dialog))
            ],
            open=True
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()