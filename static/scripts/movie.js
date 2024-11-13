document.addEventListener("DOMContentLoaded", async () => {
    const searchField = document.getElementById("search-bar");
    searchField.addEventListener("input", loadSearchResults_movie);
    searchField.addEventListener("click", loadSearchResults_movie);
    searchField.addEventListener("blur", clearResults_movie);
});
async function loadSearchResults_movie() {
    const searchField = document.getElementById("search-bar");
    const title = searchField.value;
    const url = `https://api.themoviedb.org/3/search/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&query=${title}`;
    const response = await fetch(url);
    const index = await validateJSON_movie(response);
    const resultsDiv = document.getElementById("search-results");
    var i = 0;
    if (Array.isArray(index["results"])) {
        resultsDiv.innerHTML = "";
        for (const movie of index["results"]) {
            if (i < 7) {
                const link = document.createElement("a");
                link.innerText = movie["title"];
                link.href = `/movie/${movie["id"]}`;
                resultsDiv.appendChild(link);
                i++;
            }
        }
    }
    if (searchField.value === "") {
        resultsDiv.innerHTML = "";
    }
}
async function validateJSON_movie(response) {
    if (response.ok) {
        return response.json();
    }
    else {
        return Promise.reject(response);
    }
}
async function clearResults_movie() {
    document.addEventListener("click", (event) => {
        const targetElement = event.target;
        if (targetElement.id !== "search-results") {
            const resultsDiv = document.getElementById("search-results");
            resultsDiv.innerHTML = "";
        }
    });
}
