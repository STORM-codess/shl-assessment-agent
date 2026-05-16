import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

BASE_URL = "https://www.shl.com"

CATALOG_URL = (
    "https://www.shl.com/products/product-catalog/?start={}&type=1&type=1"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}


def get_catalog_page(start):

    url = CATALOG_URL.format(start)

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            print(f"Failed for page: {url}")
            return None

        return response.text

    except requests.exceptions.RequestException as e:
        print(f"Request error for {url}: {e}")
        return None


def extract_links(html):

    soup = BeautifulSoup(html, "lxml")

    extracted_links = []

    for a_tag in soup.find_all("a", href=True):

        href = a_tag["href"]

        if "/products/product-catalog/view/" in href:

            full_url = urljoin(BASE_URL, href)

            if full_url not in extracted_links:
                extracted_links.append(full_url)

    return extracted_links


def collect_all_links():

    all_links = []

    for start in range(0, 373, 12):

        print(f"\nScraping page starting at {start}")

        html = get_catalog_page(start)

        if html:

            links = extract_links(html)

            # Handle first page separately
            if start == 0:

                print("Removing first 12 unwanted links from first page...")

                links = links[12:]

            print(f"Found {len(links)} assessment links")

            all_links.extend(links)

        time.sleep(1)

    # Remove duplicates + sort
    unique_links = sorted(list(set(all_links)))

    return unique_links


def save_links(links):

    with open(
        "data/raw/assessment_links.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(links, f, indent=4)

    print(
        f"\nSaved {len(links)} links to "
        f"data/raw/assessment_links.json"
    )


if __name__ == "__main__":

    all_links = collect_all_links()

    print(f"\nTotal unique assessment links: {len(all_links)}")

    print("\nSample links:\n")

    for link in all_links[:20]:
        print(link)

    save_links(all_links)