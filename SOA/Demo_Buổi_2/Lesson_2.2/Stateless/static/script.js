const token = "demo_token_123";

function loadBooks() {
    fetch("/api/books")
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, book_id: id })
    })
    .then(res => res.json())
    .then(msg => document.getElementById("result").textContent = msg.message || msg.error);
}

function returnBook() {
    const id = Number(document.getElementById("bookId").value);
    fetch("/api/return", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, book_id: id })
    })
    .then(res => res.json())
    .then(msg => document.getElementById("result").textContent = msg.message || msg.error);
}
