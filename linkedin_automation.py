import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DATA_PATH = "chroma_data/"
EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "comments_gladteknisk_linkedin_op"

class LoginInputNotFoundError(Exception):
    pass

class ThreadNavigationError(Exception):
    pass

def query_collection(collection):
    """Foretag request til ChromaDB-collection."""    
    query_results = collection.query(
        query_texts=["intiativ"],
        include=["documents", "distances"],
        n_results=1,
    )
    return query_results


def query_by_name_collection(collection):
    """Foretag request til ChromaDB-collection baseret på forfatternavn."""
    query_results = collection.query(
        query_texts=["sparring", "intiativ"],
        where={"author": {"$in": ["Laurits Wehding", "Mathias Risom"]}},
        n_results=1,
    )
    return query_results


def test_query():
    """Test request til collection."""
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    collection = client.get_collection(COLLECTION_NAME)
    query_results_by_name = query_by_name_collection(collection)
    print(query_results_by_name)


def initialize_chromadb_collection():
    """Initialiser ChromaDB-collection."""
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    try:
        collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_func,
                                               metadata={"hnsw:space": "cosine"})
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

    return collection


def extract_comments(collection, driver, url):
    """Udtræk kommentarer fra LinkedIn-tråd og indsæt i ChromaDB-collection."""
    driver.get(url)
    time.sleep(6)
    try:
        comment_elements = driver.find_elements(By.XPATH, "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/div/section/div/div/div/div/div[6]/div[3]/div[3]/div/article")
    except Exception as e:
        raise ThreadNavigationError(f"Fejl ved at finde kommentarelementer: {e}")

    for i, comment_element in enumerate(comment_elements):
        author = comment_element.find_element(By.CSS_SELECTOR, ".comments-post-meta__name-text > span:nth-child(1) > span:nth-child(1)").text
        timestamp = comment_element.find_element(By.CLASS_NAME, "comments-comment-item__timestamp").text
        content = comment_element.find_element(By.CLASS_NAME, "comments-comment-item__main-content").text

        try:
            collection.add(
                ids=[f"id{i}"],
                documents=[content],
                metadatas=[{"author": author, "timestamp": timestamp}]
            )
        except Exception as e:
            print("Error inserting comment:", e)


def main(username, password, url):
    """Hovedfunktion."""
    collection = initialize_chromadb_collection()
    driver = webdriver.Chrome()

    try:
        driver.get("https://www.linkedin.com/login")
        time.sleep(5)
        try:
            driver.find_element(By.ID, "username").send_keys(username)
            driver.find_element(By.ID, "password").send_keys(password)
            sign_in_button = driver.find_element(By.XPATH, "//button[@aria-label='Log ind']")
        except Exception as e:
            raise LoginInputNotFoundError(f"Fejl ved at finde login-inputs: {e}")

        sign_in_button.click()
        time.sleep(10)
        extract_comments(collection, driver, url)
    finally:
        driver.quit()
        test_query()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Brug: python linkedin_automation.py <brugernavn> <adgangskode> <linkedin_tråd_url>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
