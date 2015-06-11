def update_widget(down_speed,up_speed,users):
    Speed_Adapter.DOWN_WIDGET.set_text(down_speed)
    Speed_Adapter.UP_WIDGET.set_text(up_speed)
    Speed_Adapter.USERS_WIDGET.set_text('Users Online: '+users)
    
    
class Speed_Adapter():
    
    UP_WIDGET = None
    DOWN_WIDGET = None
    USERS_WIDGET = None
    
    def set_widget(self,down_label,up_label,users_label):
        Speed_Adapter.DOWN_WIDGET = down_label
        Speed_Adapter.UP_WIDGET = up_label
        Speed_Adapter.USERS_WIDGET = users_label
