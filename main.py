import asyncio
import random

from termcolor import cprint

from settings import USE_PROXY, SLEEP_TIME
from aiohttp import ClientSession, TCPConnector
from aiohttp_socks import ProxyConnector


def get_user_agent():
    random_version = f"{random.uniform(520, 540):.2f}"
    return (f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random_version} (KHTML, like Gecko)'
            f' Chrome/126.0.0.0 Safari/{random_version} Edg/126.0.0.0')


async def send_airtable(email_address, username, proxy):

    cprint(f'Starting submit your email: {email_address} and username: {username}')

    url = "https://sigma.wormhole.com/api/airtable"

    headers = {
        "accept": "*/*",
        "accept-language": "ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Chromium\";v=\"126\", \"Not;A=Brand\";v=\"23\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "referrer": "https://sigma.wormhole.com/",
        "referrerPolicy": "strict-origin-when-cross-origin",
        'User-Agent': get_user_agent()
    }

    payload = {
        "emailAddress": email_address,
        "firstName": username,
        "keepInformed": True
    }

    async with ClientSession(
            connector=ProxyConnector.from_url(f"http://{proxy}") if USE_PROXY else TCPConnector()
    ) as session:
        async with session.request(
                method="POST", url=url, headers=headers, json=payload
        ) as response:
            if response.status in [200, 201]:
                data = await response.json()

                if data.get('message') == 'Record added successfully':
                    cprint('Successfully submitted your email + username', 'light_green')
                    return True
            cprint(
                f"Bad request to WormholeSigma API. "
                f"Response status: {response.status}. Status: {response.status}. Response: {await response.text()}", 'light_red')


async def main():
    with open('emails.txt') as file:
        email_addresses = file.readlines()

    with open('usernames.txt') as file:
        usernames = file.readlines()

    with open('proxies.txt') as file:
        proxies = file.readlines()

    for index, email in enumerate(email_addresses):
        username = usernames[index].strip()
        proxy = proxies[index].strip()
        email = email.strip()

        while True:
            try:
                await send_airtable(email, username, proxy)
                break
            except Exception as error:
                cprint(error, 'light_red')
                cprint(f"Will try change to change proxy. Old: {proxy}", 'light_cyan')
                proxy = random.choice(proxies)
                cprint(f"Successfully changed proxy. New proxy: {proxy}", 'light_cyan')

        await asyncio.sleep(random.randint(*SLEEP_TIME))

    cprint('Successfully submitted all your emails!', 'light_green')

asyncio.run(main())
