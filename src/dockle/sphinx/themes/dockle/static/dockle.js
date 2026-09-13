(() => {
  "use strict";

  const root = document.documentElement;
  const storageKey = "dockle-color-scheme";
  let storedScheme = null;

  try {
    storedScheme = localStorage.getItem(storageKey);
  } catch {
    // Storage can be unavailable for local files or hardened browser policies.
  }

  if (storedScheme === "light" || storedScheme === "dark") {
    root.dataset.colorScheme = storedScheme;
  }

  const currentScheme = () => {
    if (root.dataset.colorScheme) {
      return root.dataset.colorScheme;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  document.querySelectorAll("[data-dockle-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const next = currentScheme() === "dark" ? "light" : "dark";
      root.dataset.colorScheme = next;
      try {
        localStorage.setItem(storageKey, next);
      } catch {
        // The in-page selection still works for the current page.
      }
    });
  });

  document.querySelectorAll("[data-dockle-menu-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const open = root.toggleAttribute("data-sidebar-open");
      button.setAttribute("aria-expanded", String(open));
    });
  });

  document.querySelectorAll("[data-dockle-search]").forEach((input) => {
    const results = document.querySelector(`[data-dockle-search-results="${input.id}"]`);
    if (!results) {
      return;
    }

    let documents;
    const loadDocuments = async () => {
      if (!documents) {
        const response = await fetch(input.dataset.dockleSearch);
        if (!response.ok) {
          throw new Error(`Search index returned ${response.status}`);
        }
        documents = (await response.json()).docs || [];
      }
      return documents;
    };

    input.addEventListener("input", async () => {
      const query = input.value.trim().toLocaleLowerCase();
      results.replaceChildren();
      results.hidden = query.length < 2;
      if (results.hidden) {
        return;
      }

      try {
        const matches = (await loadDocuments())
          .filter((document) => `${document.title} ${document.text}`.toLocaleLowerCase().includes(query))
          .slice(0, 8);
        for (const match of matches) {
          const item = document.createElement("li");
          const link = document.createElement("a");
          link.href = new URL(`${input.dataset.dockleRoot}/${match.location}`, document.baseURI);
          link.textContent = match.title;
          item.append(link);
          results.append(item);
        }
        if (!matches.length) {
          const item = document.createElement("li");
          item.textContent = "No matching pages";
          results.append(item);
        }
      } catch {
        const item = document.createElement("li");
        item.textContent = "Search is unavailable";
        results.append(item);
      }
    });
  });
})();
