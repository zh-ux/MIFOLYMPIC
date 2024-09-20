from flet import *
from threading import Lock
from pages.first_page import FirstPage
from pages.referee_page import RefereePage
from pages.all_tasks import AllTasks
from pages.previous_tasks import PreviousTasks
from pages.current_task import CurrentTasks
from pages.create_task import CreateTask
from pages.scorer_page import ScorerPage
from pages.task_in_progress import TaskInProgress


def main(page: Page):
    def navigate_to(page_name, username=None, start_timer=None):
        for control in pages:
            control.visible = control.name == page_name
            if control.visible:
                control.reset()
            if page_name == "Scorer" and isinstance(control, ScorerPage):
                control.page = page
                if username:
                    control.load_tasks(username)
            elif page_name == "All tasks" and isinstance(control, AllTasks):
                control.page = page
                control.load_tasks()
            elif page_name == "Task in progress" and isinstance(control, TaskInProgress):
                control.page = page
                if username:
                    control.position(page)
                    control.load_tasks(username)
                    control.init_page(page)
            elif page_name == "Current tasks" and isinstance(control, CurrentTasks):
                control.page = page
                if start_timer:
                    control.start_timer()
        page.update()   
    
    mutex = Lock()
    
    first_page = FirstPage(navigate_to, mutex)
    referee_page = RefereePage(navigate_to)
    all_tasks = AllTasks(navigate_to, mutex)
    previous_tasks = PreviousTasks(navigate_to, mutex)
    current_tasks = CurrentTasks(navigate_to, mutex)
    create_task = CreateTask(navigate_to, mutex)
    scorer_page = ScorerPage(navigate_to, mutex)
    task_in_progress = TaskInProgress(navigate_to, mutex)
    
    pages = [first_page, referee_page, all_tasks, previous_tasks, current_tasks, create_task, scorer_page, task_in_progress]
    
    for control in pages:
        control.visible = False
    first_page.visible = True
    
    page.add(first_page, referee_page, all_tasks, previous_tasks, current_tasks, create_task, scorer_page, task_in_progress)

app(target=main, assets_dir="assets")