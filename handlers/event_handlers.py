from handlers.on_click_handler import handle_click

class EventHandlers:
    def __init__(self, viewer):
        self.viewer = viewer

    def on_click(self, event):
        handle_click(self.viewer, event)

    def on_drag(self, event):
        pass  

    def on_release(self, event):
        pass  

    
