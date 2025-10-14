let searchTimeout = null;

function search(page = 1) {
    const qEl = document.getElementById("q");
    const query = (qEl && qEl.value ? qEl.value : "").trim(); // trim đầu/cuối
    fetch(`/api/books?q=${encodeURIComponent(query)}&page=${page}`)
        .then(res => res.json())
        .then(data => {
            const resultDiv = document.getElementById("result");
            resultDiv.innerHTML = "";

            let html = `
                <table>
                    <tr><th>ID</th><th>Tiêu đề</th><th>Tác giả</th><th>Thể loại</th><th>Năm XB</th><th>Trạng thái</th></tr>
            `;
            (data.items || []).forEach(b => {
                html += `
                    <tr>
                        <td>${b.id}</td>
                        <td>${b.title}</td>
                        <td>${b.author}</td>
                        <td>${b.category}</td>
                        <td>${b.published_year}</td>
                        <td>${b.status === 'available' ? 'Có sẵn' : 'Đã mượn'}</td>
                    </tr>`;
            });
            html += "</table>";

            html += `<div class="pager">Trang ${data.page}/${data.total_pages} `;
            if (data.page > 1)
                html += `<button onclick="search(${data.page - 1})">Trước</button>`;
            if (data.page < data.total_pages)
                html += `<button onclick="search(${data.page + 1})">Tiếp</button>`;
            html += "</div>";

            resultDiv.innerHTML = html;
        })
        .catch(err => {
            console.error("Lỗi khi fetch:", err);
        });
}

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("q");
    if (input) {
        input.addEventListener("input", () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => search(1), 300);
        });
    }
    search(1);
});
