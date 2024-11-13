document.addEventListener("DOMContentLoaded", async () => {
    loadHomePage();
    const searchField = <HTMLInputElement> document.getElementById("search-bar");
    searchField.addEventListener("input", loadSearchResults);
});

async function loadSearchResults() {
    // Get the search field and its current value
    const searchField = <HTMLInputElement> document.getElementById("search-bar");
    const title = searchField.value;
    // Create a url to query the API
    const url = `https://api.themoviedb.org/3/search/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&query=${title}`;
    // Fetch the data
    const response = await fetch(url);
    const index = await validateJSON(response);
    // Insert entries into the page for each movie
    const resultsDiv = <HTMLDivElement> document.getElementById("search-results");
    // Clear previous search results
    var i = 0;
    if (Array.isArray(index["results"])) {
        resultsDiv.innerHTML = "";
        for (const movie of index["results"]) {
            if (i < 7){
                const link = document.createElement("a");
                link.innerText = movie["title"];
                link.href=`/movie/${movie["id"]}`
                resultsDiv.appendChild(link);
                i++;
            }
        }
    }
    if (searchField.value === ""){
        resultsDiv.innerHTML = "";
    }
}

async function validateJSON(response: Response): Promise<any> {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}

async function loadHomePage() {
    // Action Movies
    var url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=28`;
    loadUrl(url, "scroll-box-action");
    // Comedy Movies
    url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=35`;
    loadUrl(url, "scroll-box-comedy");
    // Romance Movies
    var url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=10749`;
    loadUrl(url, "scroll-box-romance");
    // Western Movies
    url = `https://api.themoviedb.org/3/discover/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&with_genres=37`;
    loadUrl(url, "scroll-box-western");
}

async function loadUrl(url: string, box: string) {
    const response = await fetch(url);
    const index = await validateJSON(response);
    // Insert entries into the page for each movie
    const actionDiv = <HTMLDivElement> document.getElementById(box);
    // Clear previous search results
    var i = 0;
    if (Array.isArray(index["results"])) {
        for (const movie of index["results"]) {
            if (i < 10){
                // Create a section
                const section = document.createElement("section");
                section.id = "poster-section";
                // Create a link
                const link = document.createElement("a");
                link.href = `/movie/${movie["title"]}`;
                // Create an image to go in section
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