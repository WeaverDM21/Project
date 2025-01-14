document.addEventListener("DOMContentLoaded", async () => {
    loadHomePage();
    const searchField = document.getElementById("search-bar");
    searchField.addEventListener("input", loadSearchResults);
    searchField.addEventListener("click", loadSearchResults);
    searchField.addEventListener("blur", clearResults);
    const resultsDiv = document.getElementById("search-results");
    resultsDiv.style.display = "none";
});
async function loadSearchResults() {
    const searchField = document.getElementById("search-bar");
    const title = searchField.value;
    const url = `https://api.themoviedb.org/3/search/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&query=${title}`;
    const response = await fetch(url);
    const index = await validateJSON(response);
    const resultsDiv = document.getElementById("search-results");
    var i = 0;
    if (Array.isArray(index["results"])) {
        resultsDiv.innerHTML = "";
        resultsDiv.style.display = "block";
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
        resultsDiv.style.display = "none";
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
async function loadHomePage() {
    var url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=28`;
    loadUrl(url, "scroll-box-action");
    url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=35`;
    loadUrl(url, "scroll-box-comedy");
    var url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=10749`;
    loadUrl(url, "scroll-box-romance");
    url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=37`;
    loadUrl(url, "scroll-box-western");
    url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=80`;
    loadUrl(url, "scroll-box-crime");
    url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=10751`;
    loadUrl(url, "scroll-box-family");
    url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=9648`;
    loadUrl(url, "scroll-box-mystery");
}
async function loadUrl(url, box) {
    const response = await fetch(url);
    const index = await validateJSON(response);
    const actionDiv = document.getElementById(box);
    var i = 0;
    if (Array.isArray(index["results"])) {
        for (const movie of index["results"]) {
            if (i < 10 && movie["adult"] === false) {
                const section = document.createElement("section");
                section.id = "poster-section";
                const link = document.createElement("a");
                link.href = `/movie/${movie["id"]}`;
                const image = document.createElement("img");
                image.src = `https://image.tmdb.org/t/p/w500/${movie["poster_path"]}`;
                image.id = "poster-image";
                link.appendChild(image);
                section.appendChild(link);
                actionDiv.appendChild(section);
            }
        }
    }
}
async function clearResults() {
    document.addEventListener("click", (event) => {
        const targetElement = event.target;
        if (targetElement.id !== "search-results") {
            const resultsDiv = document.getElementById("search-results");
            resultsDiv.innerHTML = "";
            resultsDiv.style.display = "none";
        }
    });
}
