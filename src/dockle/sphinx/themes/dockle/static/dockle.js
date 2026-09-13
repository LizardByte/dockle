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
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
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

  const searchRoot = document.querySelector("[data-dockle-universal-search]");
  const logoUrl = searchRoot?.dataset.dockleLogoUrl;
  if (logoUrl) {
    const brandSelectors = [
      ".dockle-brand a",
      ".dockle-mobile-header a",
      ".dockle-compat-brand",
      "#projectname",
    ];
    document.querySelectorAll(brandSelectors.join(",")).forEach((brand) => {
      if (brand.querySelector(".dockle-logo")) {
        return;
      }
      const logo = document.createElement("img");
      logo.className = "dockle-logo";
      logo.src = logoUrl;
      logo.alt = "";
      brand.prepend(logo);
    });
  }

  const alertTypes = new Set([
    "note",
    "tip",
    "important",
    "warning",
    "caution",
  ]);
  document.querySelectorAll("blockquote").forEach((quote) => {
    const first = quote.firstElementChild;
    if (!first) {
      return;
    }
    const match = first.textContent.trim().match(/^\[!(\w+)\]/i);
    const type = match?.[1].toLocaleLowerCase();
    if (!type || !alertTypes.has(type)) {
      return;
    }
    first.innerHTML = first.innerHTML.replace(/^\s*\[!\w+\]\s*/i, "");
    if (!first.textContent.trim()) {
      first.remove();
    }
    quote.classList.add("dockle-alert", `dockle-alert-${type}`);
    const title = document.createElement("p");
    title.className = "dockle-alert-title";
    title.textContent = type[0].toLocaleUpperCase() + type.slice(1);
    quote.prepend(title);
  });

  const normalize = (value) => value.toLocaleLowerCase();
  const score = (entry, terms) => {
    const title = normalize(entry.title);
    const text = normalize(entry.text);
    return terms.reduce((total, term) => {
      if (title === term) {
        return total + 20;
      }
      if (title.includes(term)) {
        return total + 8;
      }
      if (text.includes(term)) {
        return total + 1;
      }
      return -1000;
    }, 0);
  };

  document.querySelectorAll("[data-dockle-search]").forEach((input) => {
    const selector = `[data-dockle-search-results="${input.id}"]`;
    const results = document.querySelector(selector);
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

    const closeResults = () => {
      results.hidden = true;
      results.replaceChildren();
    };

    input.addEventListener("input", async () => {
      const query = input.value.trim();
      const terms = normalize(query).split(/\s+/).filter(Boolean);
      results.replaceChildren();
      results.hidden = query.length < 2;
      if (results.hidden) {
        return;
      }

      try {
        const matches = (await loadDocuments())
          .map((entry) => ({ entry, score: score(entry, terms) }))
          .filter((match) => match.score >= 0)
          .sort((left, right) => right.score - left.score)
          .slice(0, 8);
        for (const match of matches) {
          const item = document.createElement("li");
          const link = document.createElement("a");
          const rootPath = input.dataset.dockleRoot.replace(/\/?$/, "/");
          link.href = new URL(
            `${rootPath}${match.entry.location}`,
            document.baseURI,
          );
          const title = document.createElement("strong");
          title.textContent = match.entry.title;
          link.append(title);
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

    input.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeResults();
        input.blur();
      }
    });
    document.addEventListener("click", (event) => {
      if (!searchRoot?.contains(event.target)) {
        closeResults();
      }
    });
  });
})();
