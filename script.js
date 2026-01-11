// Load precomputed subtitles JSON
fetch("data/subs.json")
  .then(response => response.json())
  .then(subs => {
    const container = document.getElementById("subtitles");

    subs.forEach(sub => {
      const lineDiv = document.createElement("div");
      lineDiv.className = "subtitle";

      sub.tokens.forEach(token => {
        const span = document.createElement("span");
        span.className = "word";
        span.textContent = token.text;

        // When clicked, alert the word ID
        span.addEventListener("click", () => {
          alert(`Word ID: ${token.id}`);
        });

        lineDiv.appendChild(span);
      });

      container.appendChild(lineDiv);
    });
  })
  .catch(err => console.error("Error loading subtitles:", err));
