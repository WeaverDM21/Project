document.addEventListener("DOMContentLoaded", async () => {
    const searchField = <HTMLInputElement> document.getElementById("search-bar");
    searchField.addEventListener("input", loadSearchResults);

});

async function loadSearchResults() {
    // Get the search field and its current value
    const searchField = <HTMLInputElement> document.getElementById("search-bar");
    const title = searchField.value;
    // Create a url to query the API
    const url = `http://www.omdbapi.com/?s=${title}&apikey=fafe5690`;
    // Fetch the data
    const response = await fetch(url);
    const index = await validateJSON(response);
    // Insert entries into the page for each movie
    const resultsDiv = <HTMLDivElement> document.getElementById("search-results");
    // Clear previous search results
    if (Array.isArray(index.Search)) {
        resultsDiv.innerHTML = "";
        for (const movie of index.Search) {
            const link = document.createElement("a");
            link.innerText = movie["Title"];
            link.href=`/movie/${movie["Title"]}`
            resultsDiv.appendChild(link);
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