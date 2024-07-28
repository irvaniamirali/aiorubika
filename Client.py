import codecs
import json
from DataTools import DataTools
import asyncio
from login import Login
class Client:
    def __init__(self, session_name: str = None, auth: str = None, private_key: str = None) -> None:
        self.session_name = session_name
        self.datatools = DataTools()
        if session_name != None:
            try:
                with codecs.open(f"{session_name}.json", "r", encoding="utf-8") as file:
                    data_session = json.load(file)
                    self.auth = data_session[1]
                    self.private_key = data_session[1]
            except:
                self.login = Login(self.session_name)
                asyncio.run(self.login.login())       
                with codecs.open(f"{session_name}.json", "r", encoding="utf-8") as file:
                    data_session = json.load(file)
                self.auth = data_session[1]
                self.private_key = data_session[1]
        else:
            self.auth = auth
            self.private_key = private_key
a = Client(session_name="taha")        
        