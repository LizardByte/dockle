(() => {
  "use strict";

  /*
   * Icons are adapted from Lucide 1.43.0 (ISC). Only the paths used by
   * Dockle are embedded so generated documentation remains self-contained.
   */
  const iconNodes = {
    "arrow-left": [
      ["path", { d: "m12 19-7-7 7-7" }],
      ["path", { d: "M19 12H5" }],
    ],
    "arrow-right": [
      ["path", { d: "M5 12h14" }],
      ["path", { d: "m12 5 7 7-7 7" }],
    ],
    "circle-alert": [
      ["circle", { cx: "12", cy: "12", r: "10" }],
      ["line", { x1: "12", x2: "12", y1: "8", y2: "12" }],
      ["line", { x1: "12", x2: "12.01", y1: "16", y2: "16" }],
    ],
    "circle-x": [
      ["circle", { cx: "12", cy: "12", r: "10" }],
      ["path", { d: "m15 9-6 6" }],
      ["path", { d: "m9 9 6 6" }],
    ],
    "external-link": [
      ["path", { d: "M15 3h6v6" }],
      ["path", { d: "M10 14 21 3" }],
      ["path", { d: "M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" }],
    ],
    eye: [
      ["path", { d: "M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" }],
      ["circle", { cx: "12", cy: "12", r: "3" }],
    ],
    flame: [["path", { d: "M12 3q1 4 4 6.5t3 5.5a1 1 0 0 1-14 0 5 5 0 0 1 1-3 1 1 0 0 0 5 0c0-2-1.5-3-1.5-5q0-2 2.5-4" }]],
    info: [
      ["circle", { cx: "12", cy: "12", r: "10" }],
      ["path", { d: "M12 16v-4" }],
      ["path", { d: "M12 8h.01" }],
    ],
    lightbulb: [
      ["path", { d: "M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 1.5 2.5" }],
      ["path", { d: "M9 18h6" }],
      ["path", { d: "M10 22h4" }],
    ],
    "list-todo": [
      ["path", { d: "M13 5h8" }],
      ["path", { d: "M13 12h8" }],
      ["path", { d: "M13 19h8" }],
      ["path", { d: "m3 17 2 2 4-4" }],
      ["rect", { x: "3", y: "4", width: "6", height: "6", rx: "1" }],
    ],
    menu: [
      ["path", { d: "M4 5h16" }],
      ["path", { d: "M4 12h16" }],
      ["path", { d: "M4 19h16" }],
    ],
    monitor: [
      ["rect", { width: "20", height: "14", x: "2", y: "3", rx: "2" }],
      ["line", { x1: "8", x2: "16", y1: "21", y2: "21" }],
      ["line", { x1: "12", x2: "12", y1: "17", y2: "21" }],
    ],
    moon: [["path", { d: "M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401" }]],
    "octagon-alert": [
      ["path", { d: "M12 16h.01" }],
      ["path", { d: "M12 8v4" }],
      ["path", { d: "M15.312 2a2 2 0 0 1 1.414.586l4.688 4.688A2 2 0 0 1 22 8.688v6.624a2 2 0 0 1-.586 1.414l-4.688 4.688a2 2 0 0 1-1.414.586H8.688a2 2 0 0 1-1.414-.586l-4.688-4.688A2 2 0 0 1 2 15.312V8.688a2 2 0 0 1 .586-1.414l4.688-4.688A2 2 0 0 1 8.688 2z" }],
    ],
    search: [
      ["path", { d: "m21 21-4.34-4.34" }],
      ["circle", { cx: "11", cy: "11", r: "8" }],
    ],
    sun: [
      ["circle", { cx: "12", cy: "12", r: "4" }],
      ["path", { d: "M12 2v2" }],
      ["path", { d: "M12 20v2" }],
      ["path", { d: "m4.93 4.93 1.41 1.41" }],
      ["path", { d: "m17.66 17.66 1.41 1.41" }],
      ["path", { d: "M2 12h2" }],
      ["path", { d: "M20 12h2" }],
      ["path", { d: "m6.34 17.66-1.41 1.41" }],
      ["path", { d: "m19.07 4.93-1.41 1.41" }],
    ],
    "triangle-alert": [
      ["path", { d: "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" }],
      ["path", { d: "M12 9v4" }],
      ["path", { d: "M12 17h.01" }],
    ],
  };

  const renderIcon = (host) => {
    const iconName = host.dataset.lucide.trim();
    const nodes = iconNodes[iconName];
    if (!nodes) {
      return;
    }
    host.dataset.lucide = iconName;
    const namespace = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(namespace, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");
    svg.classList.add("lucide", `lucide-${iconName}`);
    for (const [tag, attributes] of nodes) {
      const child = document.createElementNS(namespace, tag);
      for (const [name, value] of Object.entries(attributes)) {
        child.setAttribute(name, value);
      }
      svg.append(child);
    }
    host.replaceChildren(svg);
  };

  const renderIcons = (scope = document) => {
    scope.querySelectorAll("[data-lucide]").forEach(renderIcon);
  };

  const root = document.documentElement;
  const storageKey = "dockle-color-scheme";
  const colorPreference = window.matchMedia("(prefers-color-scheme: dark)");
  const themeModes = ["auto", "light", "dark"];
  let storedScheme = null;

  const isComponentReference = Boolean(document.querySelector("#component-reference"))
    || [...document.querySelectorAll("h1, h2")]
      .some((heading) => heading.textContent.trim() === "Component reference");
  if (isComponentReference) {
    root.classList.add("dockle-component-reference");
  }
  if (isComponentReference && root.dataset.dockleFramework === "jsdoc") {
    document.querySelectorAll("body > nav a").forEach((link) => {
      if (link.textContent.trim().toLocaleLowerCase() === "showcase") {
        link.textContent = "Component reference";
      }
    });
  }

  try {
    storedScheme = localStorage.getItem(storageKey);
  } catch {
    // Storage can be unavailable for local files or hardened browser policies.
  }

  if (storedScheme === "light" || storedScheme === "dark") {
    root.dataset.colorScheme = storedScheme;
  }

  const selectedScheme = () => {
    if (root.dataset.colorScheme === "light" || root.dataset.colorScheme === "dark") {
      return root.dataset.colorScheme;
    }
    return "auto";
  };

  const resolvedScheme = () => {
    if (root.dataset.colorScheme) {
      return root.dataset.colorScheme;
    }
    return colorPreference.matches ? "dark" : "light";
  };

  const updateThemeButtons = () => {
    const selected = selectedScheme();
    const selectedIndex = themeModes.indexOf(selected);
    const next = themeModes[(selectedIndex + 1) % themeModes.length];
    const icons = { auto: "monitor", light: "sun", dark: "moon" };
    document.querySelectorAll("[data-dockle-theme-toggle]").forEach((button) => {
      const icon = button.querySelector("[data-lucide]");
      const resolved = selected === "auto" ? ` (${resolvedScheme()})` : "";
      button.setAttribute(
        "aria-label",
        `Color scheme: ${selected}${resolved}. Switch to ${next}`,
      );
      button.title = button.getAttribute("aria-label");
      if (icon) {
        icon.dataset.lucide = icons[selected];
        renderIcon(icon);
      }
    });
  };

  document.querySelectorAll("[data-dockle-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const currentIndex = themeModes.indexOf(selectedScheme());
      const next = themeModes[(currentIndex + 1) % themeModes.length];
      if (next === "auto") {
        delete root.dataset.colorScheme;
      } else {
        root.dataset.colorScheme = next;
      }
      try {
        if (next === "auto") {
          localStorage.removeItem(storageKey);
        } else {
          localStorage.setItem(storageKey, next);
        }
      } catch {
        // The in-page selection still works for the current page.
      }
      updateThemeButtons();
    });
  });
  colorPreference.addEventListener("change", updateThemeButtons);

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

  const alertConfig = {
    attention: ["Attention", "circle-alert"],
    caution: ["Caution", "circle-alert"],
    danger: ["Danger", "octagon-alert"],
    error: ["Error", "circle-x"],
    hint: ["Hint", "lightbulb"],
    important: ["Important", "flame"],
    note: ["Note", "info"],
    seealso: ["See also", "eye"],
    tip: ["Tip", "lightbulb"],
    todo: ["Todo", "list-todo"],
    warning: ["Warning", "triangle-alert"],
  };

  document.querySelectorAll("blockquote").forEach((quote) => {
    const first = quote.firstElementChild;
    if (!first) {
      return;
    }
    const match = first.textContent.trim().match(/^\[!(\w+)\]/i);
    const type = match?.[1].toLocaleLowerCase();
    if (!type || !alertConfig[type]) {
      return;
    }
    const marker = first.matches("p") ? first : first.querySelector(":scope > p:first-child");
    if (!marker) {
      return;
    }
    marker.innerHTML = marker.innerHTML.replace(/^\s*\[!\w+\]\s*/i, "");
    if (!marker.textContent.trim()) {
      marker.remove();
    }
    quote.classList.add("dockle-alert", `dockle-alert-${type}`);
    const title = document.createElement("p");
    title.className = "dockle-alert-title";
    title.textContent = alertConfig[type][0];
    quote.prepend(title);
  });

  const doxygenTypes = {
    attention: "caution",
    bug: "danger",
    deprecated: "warning",
    important: "important",
    note: "note",
    pre: "hint",
    remark: "tip",
    seealso: "seealso",
    todo: "todo",
    warning: "warning",
  };
  const alertSelector = [
    ".dockle-alert",
    ".admonition",
    ...Object.keys(doxygenTypes).map((type) => `dl.${type}`),
  ].join(",");
  document.querySelectorAll(alertSelector).forEach((alert) => {
    const wasDockleAlert = alert.classList.contains("dockle-alert");
    let type;
    if (!wasDockleAlert && root.dataset.dockleFramework === "doxygen") {
      const doxygenType = [...alert.classList].find((name) => doxygenTypes[name]);
      type = doxygenTypes[doxygenType];
    }
    if (!type) {
      type = [...alert.classList].find((name) => alertConfig[name]);
    }
    if (!type) {
      type = [...alert.classList]
        .map((name) => name.match(/^dockle-alert-(\w+)$/)?.[1])
        .find((name) => alertConfig[name]);
    }
    if (!type) {
      type = "note";
    }
    alert.classList.add("dockle-alert", `dockle-alert-${type}`);
    const title = alert.querySelector(":scope > .admonition-title, :scope > dt, :scope > .dockle-alert-title");
    if (!title) {
      return;
    }
    title.classList.add("dockle-alert-title");
    if (!wasDockleAlert && root.dataset.dockleFramework === "doxygen") {
      title.textContent = alertConfig[type][0];
    }
    if (!title.querySelector("[data-lucide]")) {
      const icon = document.createElement("i");
      icon.dataset.lucide = alertConfig[type][1];
      icon.setAttribute("aria-hidden", "true");
      title.prepend(document.createTextNode(" "));
      title.prepend(icon);
    }
  });

  document.querySelectorAll(".dockle-tabs").forEach((tabSet, setIndex) => {
    const details = [...tabSet.querySelectorAll(":scope > details")];
    if (!details.length) {
      return;
    }
    const tabList = document.createElement("div");
    tabList.className = "dockle-tab-list";
    tabList.setAttribute("role", "tablist");
    const panels = [];
    details.forEach((detail, tabIndex) => {
      const summary = detail.querySelector(":scope > summary");
      const button = document.createElement("button");
      const panel = document.createElement("div");
      const selected = detail.open || tabIndex === 0;
      button.type = "button";
      button.id = `dockle-tab-${setIndex}-${tabIndex}`;
      button.textContent = summary?.textContent.trim() || `Tab ${tabIndex + 1}`;
      button.setAttribute("role", "tab");
      button.setAttribute("aria-selected", String(selected));
      button.setAttribute("aria-controls", `dockle-panel-${setIndex}-${tabIndex}`);
      panel.id = `dockle-panel-${setIndex}-${tabIndex}`;
      panel.className = "dockle-tab-panel";
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", button.id);
      panel.hidden = !selected;
      [...detail.children].filter((child) => child !== summary).forEach((child) => panel.append(child));
      button.addEventListener("click", () => {
        tabList.querySelectorAll("[role=tab]").forEach((tab) => tab.setAttribute("aria-selected", String(tab === button)));
        panels.forEach((candidate) => {
          candidate.hidden = candidate !== panel;
        });
      });
      panels.push(panel);
      tabList.append(button);
      detail.replaceWith(panel);
    });
    tabSet.prepend(tabList);
  });

  const placeBuiltWithFooter = () => {
    const footer = document.querySelector("[data-dockle-built-with]");
    const destinations = {
      doxygen: "#doc-content",
      jsdoc: "#main",
      rustdoc: "main .width-limiter",
    };
    const selector = destinations[root.dataset.dockleFramework];
    const destination = selector ? document.querySelector(selector) : null;
    if (footer && destination && !destination.contains(footer)) {
      destination.append(footer);
    }
  };

  const ensureDoxygenPageToc = () => {
    if (root.dataset.dockleFramework !== "doxygen") {
      return;
    }
    let pageNav = document.querySelector("#page-nav");
    const usesNativePageToc = pageNav?.classList.contains("page-nav-panel") ?? false;
    if (!pageNav) {
      pageNav = document.createElement("aside");
      pageNav.id = "page-nav";
      document.querySelector("#container")?.append(pageNav);
    }
    pageNav.classList.add("dockle-page-toc");
    let contents = pageNav.querySelector("#page-nav-contents");
    if (!contents) {
      contents = document.createElement("div");
      contents.id = "page-nav-contents";
      pageNav.append(contents);
    }
    if (!contents.querySelector(".dockle-toc-title")) {
      const title = document.createElement("strong");
      title.className = "dockle-toc-title";
      title.textContent = "On this page";
      contents.prepend(title);
    }
    if (!contents.querySelector("a")) {
      const headings = [...document.querySelectorAll(
        "#doc-content .contents h1.doxsection, #doc-content .contents h2.groupheader, #doc-content .contents h2.memtitle, #doc-content .contents h3",
      )];
      if (!headings.length) {
        const heading = document.querySelector("#doc-content div.header .title");
        if (heading) {
          heading.id ||= "dockle-page-start";
          headings.push(heading);
        }
      }
      const list = document.createElement("ul");
      list.className = "page-outline";
      headings.forEach((heading, index) => {
        const anchor = heading.querySelector(".anchor[id]");
        heading.id ||= anchor?.id || `dockle-section-${index + 1}`;
        const item = document.createElement("li");
        const link = document.createElement("a");
        link.href = `#${heading.id}`;
        link.textContent = heading.textContent.trim();
        item.append(link);
        list.append(item);
      });
      contents.append(list);
    }
    root.classList.add("dockle-has-page-toc");
    root.classList.toggle("dockle-native-page-toc", usesNativePageToc);
  };

  const addDoxygenNavigation = () => {
    if (root.dataset.dockleFramework !== "doxygen" || !Array.isArray(globalThis.NAVTREE)) {
      return;
    }
    const pages = [];
    const seen = new Map();
    const visit = (items) => {
      items.forEach(([title, target, children]) => {
        const hasFragment = typeof target === "string" && target.includes("#");
        const pageLocation = typeof target === "string" ? target.split("#")[0] : "";
        if (!hasFragment && pageLocation.endsWith(".html")) {
          if (seen.has(pageLocation)) {
            seen.get(pageLocation).title = title;
          } else {
            const page = { location: pageLocation, title };
            seen.set(pageLocation, page);
            pages.push(page);
          }
        }
        if (Array.isArray(children)) {
          visit(children);
        }
      });
    };
    visit(globalThis.NAVTREE);
    const current = location.pathname.split("/").pop() || "index.html";
    const index = pages.findIndex((page) => page.location === current);
    const contents = document.querySelector("#doc-content .contents");
    if (index < 0 || !contents || contents.querySelector(".dockle-generated-page-links")) {
      return;
    }
    const navigation = document.createElement("nav");
    navigation.className = "dockle-page-links dockle-generated-page-links";
    navigation.setAttribute("aria-label", "Page navigation");
    const addLink = (page, direction) => {
      if (!page) {
        return;
      }
      const link = document.createElement("a");
      link.className = direction === "Previous" ? "dockle-previous" : "dockle-next";
      link.href = page.location;
      link.innerHTML = direction === "Previous"
        ? `<i data-lucide="arrow-left" aria-hidden="true"></i><span><small>${direction}</small>${page.title}</span>`
        : `<span><small>${direction}</small>${page.title}</span><i data-lucide="arrow-right" aria-hidden="true"></i>`;
      navigation.append(link);
    };
    addLink(pages[index - 1], "Previous");
    addLink(pages[index + 1], "Next");
    if (navigation.children.length) {
      contents.append(navigation);
    }
  };

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
          link.href = new URL(`${rootPath}${match.entry.location}`, document.baseURI);
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

  addDoxygenNavigation();
  placeBuiltWithFooter();
  renderIcons();
  updateThemeButtons();
  window.addEventListener("load", ensureDoxygenPageToc);
})();
