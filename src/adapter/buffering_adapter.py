try:
    from common.decorators import exc_handler
except ImportError as msg:
    print(msg)

@exc_handler
def update_widget(BUFFER_STATUS):
    Buffering_Adapter.WIDGET.set_fraction(float(BUFFER_STATUS)/100)
    if BUFFER_STATUS == 100:
        Buffering_Adapter.WIDGET.hide()

class Buffering_Adapter():

    WIDGET = None

    def set_widget(self,progress_bar):
       Buffering_Adapter.WIDGET = progress_bar
