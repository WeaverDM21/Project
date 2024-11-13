document.addEventListener("DOMContentLoaded", async () => {
    const searchField = <HTMLInputElement> document.getElementById("search-bar");
    searchField.addEventListener("input", loadSearchResults_movie);
});

async function loadSearchResults_movie() {
    // Get the search field and its current value
    const searchField = <HTMLInputElement> document.getElementById("search-bar");
    const title = searchField.value;
    // Create a url to query the API
    const url = `https://api.themoviedb.org/3/search/movie?api_key=d136d005b47c87f94a7f7245dbede8dd&query=${title}`;
    // Fetch the data
    const response = await fetch(url);
    const index = await validateJSON_movie(response);
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

async function validateJSON_movie(response: Response): Promise<any> {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }
}