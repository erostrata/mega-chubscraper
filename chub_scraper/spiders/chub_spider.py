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

            name = data['node']['name']
            char_title = data['node']['definition']['project_name']
            personality_raw = data['node']['definition']['personality']
            first_message_raw = data['node']['definition']['first_message']
            author = data['node']['fullPath']
            description = data['node']['tagline']
            pfp = data['node']['avatar_url']

            def clean_data(d):
                clean = re.sub(r'https?://\S+|!\[.*?\]\(.*?\)', '', d)
                clean = clean.replace('\r', '').replace('\n', '').replace('{{user}}', 'user').replace('\u2019', "'").replace('\u2026', '...').replace('\u2014', '-').replace('{{char}}', char_title).replace('\\"', '"')
                return clean
            
            personality = clean_data(personality_raw)
            first_message = clean_data(first_message_raw).replace('*', '').replace('{{user}}', 'you')
            author_clean = re.sub(r'/.*', '', author)

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

            json_output = json.dumps(prompt, indent=2)

            return {
                'name': name,
                'pfp': pfp,
                'author': author_clean,
                'description': description,
                'json_output': json_output
            }

        except json.JSONDecodeError:
            logging.error("Failed to decode JSON response.")
            return None
    else:
        logging.error("Failed to retrieve the data. Status code: %d", response.status_code)
        return None

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
        start_page_number = int(match.group(1))
        for page_number in range(start_page_number, 69):
            characters_data = fetch_character_list(page_number)
            if characters_data and 'data' in characters_data and 'nodes' in characters_data['data']:
                character_urls = [construct_character_url(character['fullPath']) for character in characters_data['data']['nodes']]
                if character_urls:
                    for character_url in character_urls:
                        api_url = construct_api_url(character_url)
                        data = fetch_character_data(api_url)
                        if data:
                            formatted_response = f"Name: {data['name']}\n\nPfp URL: {data['pfp']}\n\nAuthor: {data['author']}\n\nDescription: {data['description']}\n\nJSON:\n{data['json_output']}"
                            print(formatted_response)
                        else:
                            logging.error("Failed to fetch character data for URL: %s", character_url)
                else:
                    logging.error("No character URLs found on page %d.", page_number)
            else:
                logging.error("No valid character data found on page %d.", page_number)
    else:
        logging.error("No page number found in the URL.")

if __name__ == "__main__":
    main()
