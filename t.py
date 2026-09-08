from Core.security.Jwt import generate_token , JWTPayload
from Features.Auth.Domain.Entities.UserEntity import Role
import requests

token = generate_token(JWTPayload("1", "a@a.com", Role.ADMIN.value))
# print(token)


import requests

headers = {
    'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'http://127.0.0.1:8000',
    'Referer': 'http://127.0.0.1:8000/docs',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36',
    'accept': 'application/json',
    'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Google Chrome";v="152"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'access_token': token,
}

response = requests.delete(
    'http://127.0.0.1:8000/auth/user/id/24db5a12-af43-4627-b827-68f2f20fa63d',
    headers=headers,
)

print(response.status_code)
print(response.json())