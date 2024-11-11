document.addEventListener("DOMContentLoaded", async () => {
    const searchField = document.getElementById("search-bar");
    searchField.addEventListener("input", loadSearchResults);
});
async function loadSearchResults() {
    const searchField = document.getElementById("search-bar");
    const title = searchField.value;
    const url = `http://www.omdbapi.com/?s=${title}&apikey=fafe5690`;
    const response = await fetch(url);
    const index = await validateJSON(response);
    const resultsDiv = document.getElementById("search-results");
    if (Array.isArray(index.Search)) {
        resultsDiv.innerHTML = "";
        for (const movie of index.Search) {
            const link = document.createElement("a");
            link.innerText = movie["Title"];
            link.href = `/movie/${movie["Title"]}`;
            resultsDiv.appendChild(link);
        }
    }
    if (searchField.value === "") {
        resultsDiv.innerHTML = "";
    }
}
async function validateJSON(response) {
    if (response.ok) {
        return response.json();
    }
    else {
        return Promise.reject(response);
    }
}
