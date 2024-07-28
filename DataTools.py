import aiohttp
import asyncio
from json import loads , dumps
from crypto import Cryption
from random import choice
from string import ascii_lowercase,digits
import devices


class DataTools():
    def __init__(self) -> None :
        self.url_server = "https://getdcmess.iranlms.ir/"
        self.url = asyncio.run(self.urls())  # [0] = https ,[1] = wss
        self.creator_auth = lambda:"".join([choice(choice([*ascii_lowercase, *digits])) for i in range(32)])


    async def urls(self) -> tuple :
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url_server) as response:
                response = await response.json()
                status_request = response['status']
                _ = list(response['data']['API'].keys())
                https_url = response['data']['API'][choice(_)]
                wss_url = response['data']['socket'][response['data']["default_socket"]]
                if status_request == "OK":
                    return https_url, wss_url
                else:
                    raise ConnectionError("error in reqest\ncheck your net")
                

    async def send_data(self, url: str, data: dict, encoding):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=data) as response:
                response = await response.json()
                response: dict = encoding.decrypt(response.get("data_enc"))
                return loads(response)
        

    async def response_send_data (self, method: str, data_request: dict, auth: str = None, private_key: str = None, has_tmp: bool = False, url = None) -> tuple:
        auth = self.creator_auth() if auth == None else auth
        url = self.url[0] if url == None else url
        encoding = Cryption(auth = auth, private_key = private_key)
        status  = "tmp_session" if has_tmp == True else "auth"
        data_json = {"api_version": "6", status : auth, "data_enc": encoding.encrypt(dumps({"method": method,"input":data_request, "client":devices.web}))}    
        if has_tmp == True:
            response_ = await self.send_data(url=url,data=data_json, encoding=encoding)
        else:
            auth = encoding.changeAuthType(encoding.auth)
            data_json["sign"] = encoding.makeSignFromData(data_json["data_enc"])
            response_ = await self.send_data(url=url,data=data_json, encoding=encoding)    
        return response_         