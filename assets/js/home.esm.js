import Fuse from 'https://cdn.jsdelivr.net/npm/fuse.js@7.1.0/dist/fuse.mjs'

const input = document.getElementById("search");
const results = document.getElementById("results");

// prepare fuzzy searcher
const artists = await fetch("api/artists/list").then(res => res.json());
const fuse = new Fuse(artists, { keys: ["name"] });

async function search() {
    const query = input.value;
    results.innerHTML = "";

    // make sure query is at least 2 characters long
    if (query.length < 2) {
        return;
    }

    // search for artists matching the query
    const matches = fuse.search(query).slice(0, 10).map(result => result.item);

    matches.forEach(item => {
        const li = document.createElement("li");
        const link = document.createElement("a");
        link.href = `artist/${item.slug}`;
        link.textContent = item.name;

        li.appendChild(link);
        results.appendChild(li);
    });
}

await search();
input.addEventListener("keyup", search);