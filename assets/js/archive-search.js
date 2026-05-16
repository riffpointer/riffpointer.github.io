(() => {
  window.addEventListener("DOMContentLoaded", function () {
    if (typeof SimpleJekyllSearch === "undefined") return;
    SimpleJekyllSearch({
      searchInput: document.getElementById("search-input"),
      resultsContainer: document.getElementById("search-results"),
      json: "/assets/search.json"
    });
  });
})();
