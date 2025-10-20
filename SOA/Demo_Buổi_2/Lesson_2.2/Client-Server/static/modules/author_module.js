import { App } from "/static/main.js";

const AuthorModule = {
    init() {
        const btn = document.getElementById("btn-load-authors");
        if (btn) btn.onclick = this.loadAuthors;
    },
    loadAuthors() {
        fetch("/api/authors")
            .then(res => res.json())
            .then(data => {
                const list = document.getElementById("author-list");
                list.innerHTML = "";
                data.forEach(a => {
                    const li = document.createElement("li");
                    li.textContent = `${a.id}. ${a.name}`;
                    list.appendChild(li);
                });
            });
    }
};

App.register("authorModule", AuthorModule);
