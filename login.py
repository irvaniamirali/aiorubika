
from crypto import Cryption
from json import loads, load, dumps, dump
from devices import device,web
import codecs
from DataTools import DataTools


class Login:
    def __init__(self,session_name) -> None:
        self.session_name = session_name
        self.datatools = DataTools()
    def check_phone_number(self, phone_number: str = None):
        if phone_number.startswith("0"):
            if len(phone_number) == 11:
                return "98" + phone_number[1:]
            else:
                print("The phone number is in invalid")
                return None
        elif phone_number.startswith("0"):
            if len(phone_number) == 10:
                return "98" + phone_number
            else:
                print("The phone number is in invalid")
                return None
        else:
            print("The phone number is in invalid")
            return None
    

    async def send_code(self) -> tuple:
        while (number := self.check_phone_number(input("phone number : "))) is None:
            pass
        sendcode = await self.datatools.response_send_data("sendCode", {"phone_number": number  , "pass_key": None, "send_type": "SMS"},has_tmp = True)
        return number, sendcode.get("status"), sendcode.get("status_det"), sendcode.get("data").get("status"), sendcode.get("data").get("hint_pass_key"), sendcode.get("data").get("has_confirmed_recovery_email"), sendcode.get("auth"), sendcode.get("data").get('phone_code_hash')
    

    async def send_pass_key(self, result: tuple):
        password = input(f"password {result[4]}: ")
        send_status = await self.datatools.response_send_data("sendCode", {"phone_number": result[0]  , "pass_key": password, "send_type": "SMS"}, auth=result[6],has_tmp=True)
        while result[3] == 'InvalidPassKey':
            input(f"password {result[4]}: ")
            send_status = await self.datatools.response_send_data("sendCode", {"phone_number": result[0]  , "pass_key": password, "send_type": "SMS"}, auth=result[6],has_tmp=True)
        return result[0], send_status.get("status"), send_status.get("status_det"), send_status.get("data").get("status"), send_status.get("data").get("hint_pass_key"), send_status.get("data").get("has_confirmed_recovery_email"), send_status.get("auth"), send_status.get("data").get('phone_code_hash')
    
    async def check_pass_key(self):
        result = await self.send_code()
        if result[1] == 'OK' and result[3] == "SendPassKey":
            result = await self.send_pass_key(result=result)
            return result
        elif result[3] == "OK":
            return result    
        else:
            return "erorr in sigin"
    async def check_code(self):
            while len(code_login := input("code : ")) != 6:
                print("the erorr code has 6 characters")
            return code_login    
    async def signin(self):
        result = await self.check_pass_key()
        public, private = Cryption().rsaKeyGenrate()
        code_login = await self.check_code()
        result_signin = await self.datatools.response_send_data(method="signIn",data_request= {"phone_number": result[0], "phone_code_hash": result[7], "phone_code": code_login, "public_key": public}, auth=result[6], has_tmp=True)
        print(result_signin)
        if result_signin['data']['status'] == "CodeIsInvalid":
            raise ValueError(f"code is invalid")
        auth = Cryption.decryptRsaOaep(private, result_signin["data"]["auth"])
        return private, auth, result_signin,result_signin["data"]["auth"]
    async def login(self):
        result = await self.signin()
        with codecs.open(f"{self.session_name}.json", "w", encoding="utf-8") as file_auth:
            dump(result, file_auth, indent=2, ensure_ascii=True)
        result_login = await self.datatools.response_send_data(method="registerDevice", data_request=device, auth=result[1], private_key=result[0])
        return result_login
