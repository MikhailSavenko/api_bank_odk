class ExeptionSSOClose(Exception):
    """Сессия завершена статус 500"""
    
    def __init__(self, message="Сессия пользователя завершена"):
        self.message = message
        super().__init__(self.message)