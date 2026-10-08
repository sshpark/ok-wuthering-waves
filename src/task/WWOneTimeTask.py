from ok import BrowserInteraction
try:
    from ok import PostMessageInteraction
except ImportError:
    PostMessageInteraction = None
try:
    from ok import MacInteraction
except ImportError:
    MacInteraction = None
from src.task.MouseResetTask import MouseResetTask


class WWOneTimeTask:

    def run(self):
        mouse_reset_task = self.executor.get_task_by_class(MouseResetTask)
        mouse_reset_task.run()
        if PostMessageInteraction is not None and isinstance(self.executor.interaction, PostMessageInteraction):
            self.executor.interaction.activate()
        elif MacInteraction is not None and isinstance(self.executor.interaction, MacInteraction):
            self.executor.interaction.activate()
        self.sleep(0.5)
