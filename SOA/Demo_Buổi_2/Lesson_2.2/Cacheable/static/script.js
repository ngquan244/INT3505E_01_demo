// TOKEN GIẢ ĐỊNH 
const token = "demo_token_123";

//  CACHE CỤC BỘ CLIENT 
const API_CACHE = {}; 
const CACHE_DURATION = 30000; 
// 30 giây (tương ứng với max-age=30)


//  LẤY DANH SÁCH SÁCH 
function loadBooks(forceReload = false) {
    const now = Date.now();

    // Nếu có cache và chưa hết hạn => dùng cache
    if (!forceReload && API_CACHE.books && now - API_CACHE.books.time < CACHE_DURATION) {
        console.log("Dùng cache client");
        displayBooks(API_CACHE.books.data);
        return;
    }

    console.log("Gọi server /api/books...");
    fetch("/api/books")
        .then(res => {
            console.log("Server time:", res.headers.get("X-Server-Time"));
            return res.json();
        })
        .then(data => {
            API_CACHE.books = { data, time: now };
            displayBooks(data);
        });
}


// HIỂN THỊ DANH SÁCH 
function displayBooks(data) {
    const list = document.getElementById("book-list");
    list.innerHTML = "";
    data.forEach(b => {
        const li = document.createElement("li");
        li.textContent = `${b.id}. ${b.title} - ${b.available ? "Có sẵn" : "Đã mượn"}`;
        list.appendChild(li);
    });
}


// MƯỢN SÁCH 
function borrowBook() {
    const id = Number(document.getElementById("bookId").value);
    fetch("/api/borrow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, book_id: id })
    })
    .then(res => res.json())
    .then(msg => {
        document.getElementById("result").textContent = msg.message || msg.error;
        clearCache(); 
    });
}


// TRẢ SÁCH
function returnBook() {
    const id = Number(document.getElementById("bookId").value);
    fetch("/api/return", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, book_id: id })
    })
    .then(res => res.json())
    .then(msg => {
        document.getElementById("result").textContent = msg.message || msg.error;
        clearCache(); 
    });
}


// XÓA CACHE
function clearCache() {
    API_CACHE.books = null;
    document.getElementById("cache-status").textContent = "(cache đã bị xóa)";
    console.log("Cache cleared");
}
