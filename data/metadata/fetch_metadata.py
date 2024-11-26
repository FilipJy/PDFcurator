import requests

def fetch_metadata_from_isbn(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            volume_info = data["items"][0].get("volumeInfo", {})
            metadata = {
                "Title": volume_info.get("title", "N/A"),
                "Author": ", ".join(volume_info.get("authors", ["N/A"])),
                "Publisher": volume_info.get("publisher", "N/A"),
                "Language": volume_info.get("language", "N/A"),
                "ISBN": isbn,
                "Genre": ", ".join(volume_info.get("categories", ["N/A"]))
            }
            return metadata
        else:
            print("No metadata found.")
    else:
        print(f"HTTP Error: {response.status_code}")
    return None
