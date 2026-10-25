import argparse
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer

from urllib.parse import urldefrag

parser = argparse.ArgumentParser(
    description="Find link paths between Wikipedia articles."
)
parser.add_argument("-s", "--start", required=True, help="Starting topic name")
parser.add_argument("-e", "--end", required=True, help="Destination topic name")
args = parser.parse_args()

start_topic = args.start.strip().replace(" ", "_")
end_topic = args.end.strip().replace(" ", "_")


no_need = {"portal", "template", "help", "red_link"}


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
    for link in content.find_all("a", attrs={"rel": "mw:WikiLink"}):
        target_slug = link["href"]
        target_slug, _ = urldefrag(target_slug)
        target_slug = target_slug.strip().split("/")[-1]
        if (
            target_slug not in links
            and target_slug != topic_slug
            and not any(word in target_slug.lower() for word in no_need)
        ):
            links.append(target_slug.strip().split("/")[-1])

    return links


def score_function(found_links, model, target_slug_encode, visited):
    unvisited_links = [
        slug for slug in found_links
        if slug not in visited
    ]

    if not unvisited_links:
        return None

    embeddings = model.encode(unvisited_links)
    scores = model.similarity(
        embeddings,
        target_slug_encode
    ).flatten()

    best_index = scores.argmax().item()

    return unvisited_links[best_index]


# # Example run:
# found_links = extract_links(start_topic)

model = SentenceTransformer("./model")


target_slug_encode = model.encode(end_topic)
count = 0
topic = []
visited = set()
path = [start_topic]


while start_topic.lower() != end_topic.lower():

    visited.add(start_topic)

    found_links = extract_links(start_topic)

    next_topic = score_function(
        found_links,
        model,
        target_slug_encode,
        visited
    )

    if next_topic is None:
        print("No unvisited links available.")
        break

    start_topic = next_topic
    path.append(start_topic)

    print(f"Hop {len(path) - 1}: {start_topic}")

if start_topic.lower() == end_topic.lower():
    print("Destination reached!")

print("Path:", " → ".join(path))
print("Number of hops:", len(path) - 1)