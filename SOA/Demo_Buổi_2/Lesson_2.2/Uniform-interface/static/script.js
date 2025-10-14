const token = "demo_token_123";

function loadBooks() {
    fetch("/api/books", {
        headers: { "Accept": "application/json" }
    })
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("book-list");
        list.innerHTML = "";
        data.forEach(b => {
            const li = document.createElement("li");
            li.textContent = `${b.id}. ${b.title} - ${b.available ? "Có sẵn" : "Đã mượn"}`;
            list.appendChild(li);
        });
    });
}

function borrowBook() {
    const id = Number(document.getElementById("bookId").value);
    fetch("/api/borrow", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ token, book_id: id })
    })
    .then(res => res.json())
    .then(msg => document.getElementById("result").textContent = msg.message || msg.error);
}

function returnBook() {
    const id = Number(document.getElementById("bookId").value);
    fetch("/api/return", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({ token, book_id: id })
    })
    .then(res => res.json())
    .then(msg => document.getElementById("result").textContent = msg.message || msg.error);
}

function getBookById() {
    const id = Number(document.getElementById("bookId").value);
    fetch(`/api/books/${id}`)
        .then(res => res.json())
        .then(book => {
            const detail = document.getElementById("result");
            if (book.message) {
                detail.textContent = book.message;
            } else {
                detail.textContent = `${book.title} - ${book.available ? "Có sẵn" : "Đã mượn"}`;
            }
        });
}
