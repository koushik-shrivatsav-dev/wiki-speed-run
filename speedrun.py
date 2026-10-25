import argparse
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

parser = argparse.ArgumentParser(description="Find link paths between Wikipedia articles.")
parser.add_argument("-s", "--start", required=True, help="Starting topic name")
parser.add_argument("-e", "--end", required=True, help="Destination topic name")
args = parser.parse_args()

start_topic = args.start.strip().replace(" ", "_")
end_topic = args.end.strip().replace(" ", "_")

def extract_links(topic_slug: str) -> list[str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    url = f"https://en.wikipedia.org/wiki/{topic_slug}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(resp.status_code)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []

    # Target links within the main article body
    content = soup.find("div", id="bodyContent") or soup
    # print(content)
    for link in content.find_all("a"):

        target_slug = link["href"]
        if target_slug not in links and target_slug != topic_slug:
            links.append(target_slug)

    return links

# Example run:
found_links = extract_links(start_topic)
print(f"Found {len(found_links)} links on '{start_topic}'. Sample:")
for i in found_links:
    print(i)