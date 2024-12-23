import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin
from collections import deque

class CodeIgniterScraper:
    def __init__(self, base_url='https://codeigniter.com/user_guide/'):
        self.base_url = base_url
        self.visited = set()
        self.docs = {}
        self.queue = deque()
        self.output_dir = 'docs'
        os.makedirs(self.output_dir, exist_ok=True)

    def save_page(self, url, content):
        # Save individual markdown file
        filename = url.replace(self.base_url, '').replace('/', '_')
        if not filename:
            filename = 'index'
        filename = f"{filename}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)

        # Update JSON file
        self.docs[url] = content
        with open(os.path.join(self.output_dir, 'documentation.json'), 'w') as f:
            json.dump(self.docs, f, indent=2)

    def get_page_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_page(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find('div', class_='document')
        
        if not content:
            return None

        text_content = content.get_text(separator='\n', strip=True)
        
        links = []
        for a in content.find_all('a', href=True):
            href = a['href']
            if href.startswith(('http:', 'https:')):
                continue
            full_url = urljoin(url, href)
            if full_url.startswith(self.base_url):
                links.append(full_url)

        return {
            'content': text_content,
            'links': links
        }

    def crawl(self):
        self.queue.append(self.base_url)

        while self.queue:
            url = self.queue.popleft()
            
            if url in self.visited:
                continue
            
            self.visited.add(url)
            print(f"Crawling: {url}")

            html = self.get_page_content(url)
            if not html:
                continue

            parsed = self.parse_page(url, html)
            if parsed:
                self.save_page(url, parsed['content'])
                
                for link in parsed['links']:
                    if link not in self.visited:
                        self.queue.append(link)

def main():
    scraper = CodeIgniterScraper()
    scraper.crawl()

if __name__ == "__main__":
    main()