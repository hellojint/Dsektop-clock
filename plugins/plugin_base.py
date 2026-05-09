class Plugin:
    """插件基类，所有插件必须继承此类"""
    
    def __init__(self):
        self.name = "Unnamed Plugin"
        self.version = "1.0.0"
        self.description = "No description"
        self.author = "Unknown"
    
    def get_name(self):
        return self.name
    
    def get_version(self):
        return self.version
    
    def get_description(self):
        return self.description
    
    def get_author(self):
        return self.author
    
    def initialize(self, app):
        """初始化插件，接收主应用实例"""
        self.app = app
    
    def on_time_update(self, current_time):
        """时间更新时调用"""
        pass
    
    def on_weather_update(self, weather_data):
        """天气更新时调用"""
        pass
    
    def get_widget(self):
        """返回插件的UI组件（可选）"""
        return None
    
    def get_menu_items(self):
        """返回菜单项列表（可选）"""
        return []
    
    def cleanup(self):
        """插件卸载时调用"""
        pass