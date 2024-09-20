from flet import *
from pandas import *
from filelock import FileLock

class AllTasks(Container):
    def __init__(self, navigate_to, mutex):
        super().__init__(
            content=Column(
                controls=[
                    ListView(
                    controls=[
                        ],
                    horizontal=True,
                    expand=True
                    ),
                    Row(controls=[ElevatedButton(text="Back", on_click=self.back, width=300)], alignment=MainAxisAlignment.CENTER)
                    ],
                ),
            expand=True
        )
        self.name = "All tasks"
        self.navigate_to = navigate_to
        self.mutex = mutex
        self.data_table = None
        self.df = None
        
    def load_tasks(self):
        with FileLock("scorers.xlsx.lock"):
            self.df = read_excel("scorers.xlsx")
                
        columns = [DataColumn(Text(""))]
        columns.extend(DataColumn(Text(col)) for col in self.df.columns)
        
        rows = []
        
        for index, row in self.df.iterrows():
            delete_button = ElevatedButton("Delete", on_click=lambda e, idx=index: self.confirm(idx))
            cells = [DataCell(delete_button)]
            cells.extend(DataCell(Text(str(cell))) for cell in row)
            rows.append(DataRow(cells=cells))
        
        self.data_table = DataTable(
            columns=columns,
            rows=rows
        )
        
        self.content.controls[0].controls.clear()
        self.content.controls[0].controls.append(self.data_table)
        self.page.update()

    def confirm(self, idx):
        reminder_dialog = AlertDialog(
            modal=True,
            title=Text("Reminder"),
            content=Text("Do you sure you want to delete?"),
            actions=[
                TextButton("Yes", on_click=lambda e: self.delete_task(index=idx, dialog=reminder_dialog)),
                TextButton("No", on_click=lambda e: self.close_dialog(reminder_dialog))
            ],
            open=True
        )
        self.page.dialog = reminder_dialog
        self.page.update()
        
    def delete_task(self, index, dialog):
        with FileLock("scorers.xlsx.lock"):
            self.df = self.df.drop(index).reset_index(drop=True)
            self.df.to_excel("scorers.xlsx", index=False)
        self.close_dialog(dialog)
        self.load_tasks()

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
        
    def back(self, e):
        self.navigate_to("Referee")

    def reset(self):
        self.content.controls[0].controls.clear()