import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class Scraper:
    def __init__(self, provider):
        self.session = requests.Session()
        self.provider = provider.lower()
        self.base_url = f"https://www.examtopics.com/discussions/{self.provider}/"
        print(f"[Init] Scraper initialized for provider: {self.provider}")

    def get_num_pages(self):
        """Retrieve the number of pages for the provider."""
        print(f"[Get Pages] Fetching total number of discussion pages for provider: {self.provider}")
        try:
            response = self.session.get(f"{self.base_url}")
            soup = BeautifulSoup(response.content, "html.parser")
            total_pages = int(soup.find("span", {"class": "discussion-list-page-indicator"}).find_all("strong")[1].text.strip())
            print(f"[Get Pages] Total pages found: {total_pages}")
            return total_pages
        except Exception as e:
            print(f"[Get Pages] Error fetching page count: {e}")
            return 0

    def fetch_page_links(self, page, search_string):
        """Fetch links from a single page."""
        print(f"[Fetch Links] Fetching page {page}...")
        try:
            response = self.session.get(f"{self.base_url}{page}/")
            soup = BeautifulSoup(response.content, "html.parser")
            discussions = soup.find_all("a", {"class": "discussion-link"})
            links = []
            for discussion in discussions:
                # if search_string in discussion.text:
                    full_link = discussion["href"].replace("/discussions", "https://www.examtopics.com/discussions", 1)
                    links.append(full_link)
                    print(f"[Link Found] {full_link}")  # <== PRINT EACH LINK HERE
            print(f"[Fetch Links] Page {page}: Found {len(links)} matching links.")
            return links
        except Exception as e:
            print(f"[Fetch Links] Error on page {page}: {e}")
            return []

    def get_discussion_links(self, num_pages, search_string):
        """Retrieve discussion links that include the search string, using parallel requests."""
        print(f"[Discussion Links] Starting to fetch links from {num_pages} pages...")
        links = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.fetch_page_links, page, search_string) for page in range(1, num_pages + 1)]
            with tqdm(total=num_pages, desc="Fetching Links", unit="page") as pbar:
                for future in as_completed(futures):
                    page_links = future.result()
                    links.extend(page_links)
                    pbar.update(1)
        print(f"[Discussion Links] Total matching links found: {len(links)}")
        return links

def extract_topic_question(link):
    """Extract topic and question numbers from a link."""
    match = re.search(r'topic-(\d+)-question-(\d+)', link)
    if match:
        topic = int(match.group(1))
        question = int(match.group(2))
        return (topic, question)
    else:
        match_topic_only = re.search(r'topic-(\d+)-question/?$', link)
        if match_topic_only:
            topic = int(match_topic_only.group(1))
            # Assign question 9999 for links without a question number
            return (topic, 9999)
        else:
            return (None, None)

def write_grouped_links_to_file(filename, links):
    """Write the grouped links to a file."""
    print(f"[Write File] Grouping and writing links to file: {filename}")
    grouped_links = {}
    # Filter out links where extract_topic_question returns None for topic
    valid_links = [link for link in links if extract_topic_question(link)[0] is not None]  
    for link in sorted(valid_links, key=extract_topic_question):
        topic, question = extract_topic_question(link)
        if topic is not None:
            grouped_links.setdefault(topic, []).append(link)

    with open(filename, 'w') as f:
        for topic, links in grouped_links.items():
            f.write(f'Topic {topic}:\n')
            for link in links:
                f.write(f' - {link}\n')
            print(f"[Write File] Topic {topic}: {len(links)} links written.")

    print(f"[Write File] All links written successfully to {filename}.")


def write_grouped_links_to_excels(links):
    """Write links into separate Excel files per exam."""
    print(f"[Write Excel] Grouping and writing links to Excel files...")
    exam_links = {}

    # First, group links by exam
    for link in links:
        exam_match = re.search(r'exam-([a-z0-9\-]+)-topic', link)
        topic_question = extract_topic_question(link)

        if exam_match and topic_question[0] is not None:
            exam_name = exam_match.group(1)
            exam_links.setdefault(exam_name, []).append((topic_question[1], link))

    # Now write each exam's links into separate Excel files
    for exam_name, questions in exam_links.items():
        questions_sorted = sorted(questions, key=lambda x: x[0])  # Sort by question number
        df = pd.DataFrame(questions_sorted, columns=["Question Number", "Link"])
        file_name = f"{exam_name}.xlsx"
        df.to_excel(file_name, index=False)
        print(f"[Write Excel] {file_name} created with {len(questions)} questions.")

    print("[Write Excel] All Excel files created successfully ✅.")


def main():
    print("========== ExamTopics Discussion Scraper ==========")
    provider = input("Enter provider name (e.g., google, aws, etc.): ")
    scraper = Scraper(provider)

    num_pages = scraper.get_num_pages()
    print(f"[Main] Total Pages for {provider}: {num_pages}")

    if num_pages > 0:
        search_string = input("Enter exam code (e.g., PROFESSIONAL-DATABASE-ENGINEER) or 'QUIT' to exit: ").upper()
        if search_string != 'QUIT':
            links = scraper.get_discussion_links(num_pages, search_string)
            print(f"[Main] Total links matching '{search_string}': {len(links)}")

            print(f"[Main] Preparing to write Excel files...")
            write_grouped_links_to_excels(links)

            print("[Main] Scraping and file writing complete. ✅")
        else:
            print("[Main] Exiting on user request. Goodbye!")
            return
    else:
        print("[Main] No discussion pages found. Please check the provider name.")


if __name__ == "__main__":
    main()
