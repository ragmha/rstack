const results = document.querySelector("#results");
const search = document.querySelector("#search");
const categoryFilter = document.querySelector("#category-filter");
const resultCount = document.querySelector("#result-count");
const copyStatus = document.querySelector("#copy-status");
let catalog = [];

async function copy(text, button) {
  try {
    await navigator.clipboard.writeText(text);
    copyStatus.textContent = "Copied to clipboard.";
    button.textContent = "Copied";
  } catch {
    copyStatus.textContent = "Clipboard access failed. Select the text and copy it.";
    button.textContent = "Copy failed";
  }
  setTimeout(() => { button.textContent = "Copy"; }, 1500);
}

function render() {
  const query = search.value.trim().toLowerCase();
  const category = categoryFilter.value;
  const filtered = catalog.filter((item) =>
    (category === "all" || item.category === category) &&
    `${item.name} ${item.description} ${item.category}`.toLowerCase().includes(query)
  );

  resultCount.textContent = `${filtered.length} of ${catalog.length} skills`;
  results.replaceChildren();
  if (!filtered.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No matches. Try a broader search or category.";
    results.append(empty);
    return;
  }

  for (const item of filtered) {
    const card = document.createElement("article");
    card.className = "item";
    card.setAttribute("role", "listitem");
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = item.category;
    const title = document.createElement("h2");
    title.textContent = item.name;
    const description = document.createElement("p");
    description.textContent = item.description;
    const install = document.createElement("div");
    install.className = "item-install";
    const command = document.createElement("code");
    command.textContent = item.install;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Copy";
    button.setAttribute("aria-label", `Copy install command for ${item.name}`);
    button.addEventListener("click", () => copy(item.install, button));
    install.append(command, button);
    const source = document.createElement("a");
    source.className = "source";
    source.href = item.source;
    source.target = "_blank";
    source.rel = "noopener noreferrer";
    source.textContent = "View source ↗";
    card.append(badge, title, description, install, source);
    results.append(card);
  }
}

for (const button of document.querySelectorAll("[data-copy]")) {
  button.addEventListener("click", () => copy(document.getElementById(button.dataset.copy).textContent, button));
}

search.addEventListener("input", render);
categoryFilter.addEventListener("change", render);

fetch("./catalog.json")
  .then((response) => {
    if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
    return response.json();
  })
  .then((data) => {
    catalog = data.items;
    document.querySelector("#skills-command").textContent = data.install;
    document.querySelector("#mcp-config").textContent = data.mcp;
    for (const button of document.querySelectorAll("[data-copy]")) button.disabled = false;
    for (const category of [...new Set(catalog.map((item) => item.category))].sort()) {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categoryFilter.append(option);
    }
    render();
  })
  .catch((error) => {
    resultCount.textContent = "Catalog unavailable";
    const message = document.createElement("p");
    message.className = "error";
    message.textContent = error.message;
    results.replaceChildren(message);
  });
