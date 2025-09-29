import requests

BASE_URL = "http://127.0.0.1:5000"
BOOKS_URL = f"{BASE_URL}/books"
SYSTEM_URL = f"{BASE_URL}/system"
HEADERS = {"Authorization": "Bearer demo_token"}


def get_books():
    r = requests.get(BOOKS_URL, headers=HEADERS)
    print("---Danh sách sách:", r.json())


def get_book(book_id):
    r = requests.get(f"{BOOKS_URL}/{book_id}", headers=HEADERS)
    print(f"---Sách {book_id}:", r.json())


def add_book(title, author):
    data = {"title": title, "author": author}
    r = requests.post(BOOKS_URL, json=data, headers=HEADERS)
    print("---Thêm sách:", r.json())


def update_book(book_id, title=None, author=None, available=None):
    data = {}
    if title: data["title"] = title
    if author: data["author"] = author
    if available is not None: data["available"] = available
    r = requests.put(f"{BOOKS_URL}/{book_id}", json=data, headers=HEADERS)
    print(f"---Cập nhật sách {book_id}:", r.json())


def delete_book(book_id):
    r = requests.delete(f"{BOOKS_URL}/{book_id}", headers=HEADERS)
    print(f"---Xóa sách {book_id}:", r.json())


def check_layer():
    r = requests.get(f"{SYSTEM_URL}/check-layer", headers=HEADERS)
    print("---Kiểm tra Layered System:", r.json())


def get_script():
    r = requests.get(f"{SYSTEM_URL}/script", headers=HEADERS)
    print("---Script nhận được từ server:\n", r.text)


if __name__ == "__main__":
    get_books()
    add_book("Dive Into Hidden Worlds", "Jess McGeachin")
    get_books()
    get_book(1)
    update_book(1, available=False)
    delete_book(1)
    get_books()
    check_layer()
    get_script()
