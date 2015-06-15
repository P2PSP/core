def update_widget(BUFFER_STATUS):
    try:
        Buffering_Adapter.WIDGET.set_fraction(float(BUFFER_STATUS)/100)
        if BUFFER_STATUS == 100:
            Buffering_Adapter.WIDGET.hide()
    except Exception as msg:
        print(msg)
    
class Buffering_Adapter():
    
    WIDGET = None
    
    def set_widget(self,progress_bar):
       Buffering_Adapter.WIDGET = progress_bar
