import requests
import json
import logging
import re
import urllib.parse
import random


def fetch_character_list(page_number):
    api_url = f'https://api.chub.ai/search?first=24&special_mode=trending&include_forks=true&excludetopics=&search=&page={page_number}&namespace=characters&venus=true&nsfw=true&nsfw_only=false&nsfl=true&chub=true'
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'ch-api-key': 'bfac4b70-b26f-4110-a800-44563584560c',  # Update with your actual API key
        'content-type': 'application/json',
        'origin': 'https://www.chub.ai',
        'referer': 'https://www.chub.ai/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Failed to fetch character list: Status code %s", response.status_code)
        return None

def construct_character_url(character_path):
    return f"https://www.chub.ai/characters/{character_path}"


### script2 integration below: 

def fetch_character_data(url):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'ch-api-key': 'glpat-UZXEBupEVv2vMCdFDkfJ',
        'origin': 'https://chub.ai',
        'priority': 'u=1, i',
        'referer': 'https://chub.ai/',
        'samwise': 'glpat-UZXEBupEVv2vMCdFDkfJ',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()

            personality = data['node']['definition']['personality'].replace('\r', '').replace('\n', '')
            description = data['node']['definition']['description'].replace('\r', '').replace('\n', '')
            first_message = data['node']['definition']['first_message'].replace('\r', '').replace('\n', '').replace('*', '')

            prompt = {
                "type": "duo-image",
                "model": "gpt-4o-mini",
                "state": "LIVE",
                "top_p": 0.8,
                "memory": 20,
                "prompt": description + personality,
                "greeting": first_message,
                "temperature": 0.7
            }

            print(json.dumps(prompt, indent=2))
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
    else:
        print(f"Failed to retrieve the data. Status code: {response.status_code}")


def construct_api_url(base_url):
    parsed_url = urllib.parse.urlparse(base_url)

    path = parsed_url.path
    api_base_url = f"https://api.chub.ai/api{path}"

    nocache_value = random.random()
    api_url = f"{api_base_url}?full=true&nocache={nocache_value}"
    return api_url



def main():
    user_input = input("Enter the trending page link (e.g., https://www.chub.ai/?segment=trending&page=1): ")
    match = re.search(r"page=(\d+)", user_input)
    if match:
        page_number = match.group(1)
        characters_data = fetch_character_list(page_number)
        if characters_data and 'data' in characters_data and 'nodes' in characters_data['data']:
            character_urls = [construct_character_url(character['fullPath']) for character in characters_data['data']['nodes']]
            if character_urls: 
                for x in character_urls:
                    char = construct_api_url(x)
                    data = fetch_character_data(char)
                    print(data)
        else:
            logging.error("No valid character data found.")
    else:
        logging.error("No page number found in the URL.")


if __name__ == "__main__":
    main()
