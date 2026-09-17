(() => {
  "use strict";

  const renderIcons = (scope = document) => {
    const lucide = globalThis.lucide;
    if (!lucide?.createIcons || !lucide.icons) {
      return;
    }
    scope.querySelectorAll("[data-lucide]").forEach((host) => {
      host.dataset.lucide = host.dataset.lucide.trim();
    });
    lucide.createIcons({ icons: lucide.icons });
  };

  const renderIcon = (host) => {
    host.dataset.lucide = host.dataset.lucide.trim();
    renderIcons(host.ownerDocument);
  };

  const root = document.documentElement;
  const storageKey = "dockle-color-scheme";
  const colorPreference = window.matchMedia("(prefers-color-scheme: dark)");
  const themeModes = ["auto", "light", "dark"];
  let storedScheme = null;

  const configureComponentReference = () => {
    const isReference = Boolean(document.querySelector("#component-reference"))
      || [...document.querySelectorAll("h1, h2")]
        .some((heading) => heading.textContent.trim() === "Component reference");
    if (!isReference) {
      return;
    }
    root.classList.add("dockle-component-reference");
    if (root.dataset.dockleFramework !== "jsdoc") {
      return;
    }
    document.querySelectorAll("body > nav a").forEach((link) => {
      if (link.textContent.trim().toLocaleLowerCase() === "showcase") {
        link.textContent = "Component reference";
      }
    });
  };

  const loadStoredScheme = () => {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      // Storage can be unavailable for local files or hardened browser policies.
      return null;
    }
  };

  configureComponentReference();
  storedScheme = loadStoredScheme();

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
  const targetTitle = searchRoot?.dataset.dockleTargetTitle;
  if (targetTitle && root.dataset.dockleFramework === "jsdoc") {
    const home = document.querySelector("body > nav h2 a");
    if (home) {
      home.textContent = targetTitle;
    }
  }
  if (targetTitle && root.dataset.dockleFramework === "rustdoc") {
    const crate = document.querySelector(".sidebar .sidebar-crate h2 > a");
    if (crate) {
      crate.textContent = targetTitle;
    }
  }

  const normalizedPagePath = (url) => {
    const path = new URL(url, document.baseURI).pathname;
    return path.replace(/index\.html$/, "").replace(/\/$/, "");
  };
  const markCurrentNavigation = () => {
    const currentPath = normalizedPagePath(location.href);
    const selectors = {
      jsdoc: "body > nav a[href]",
      rustdoc: ".sidebar a[href]",
      sphinx: ".dockle-tree a[href]",
    };
    const selector = selectors[root.dataset.dockleFramework];
    if (!selector) {
      return;
    }
    const matches = [...document.querySelectorAll(selector)].filter((link) => {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#")) {
        return false;
      }
      const target = new URL(link.href, document.baseURI);
      return !target.hash && normalizedPagePath(target) === currentPath;
    });
    const currentLinks = root.dataset.dockleFramework === "rustdoc"
      ? matches.slice(0, 1)
      : matches;
    if (root.dataset.dockleFramework === "rustdoc") {
      matches.slice(1).forEach((link) => {
        link.closest("li")?.classList.remove("current");
      });
    }
    currentLinks.forEach((link) => {
      link.classList.add("dockle-current");
      link.setAttribute("aria-current", "page");
    });
  };
  markCurrentNavigation();
  window.addEventListener("load", markCurrentNavigation);

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
    const match = /^\[!(\w+)\]/i.exec(first.textContent.trim());
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
        .map((name) => /^dockle-alert-(\w+)$/.exec(name)?.[1])
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

  const copyText = async (text) => {
    if (!navigator.clipboard?.writeText) {
      throw new Error("The Clipboard API is unavailable");
    }
    await navigator.clipboard.writeText(text);
  };

  const codeText = (container) => {
    const lines = [...container.querySelectorAll(":scope > .line")];
    if (lines.length) {
      return lines.map((line) => line.textContent).join("\n");
    }
    const source = container.matches("pre")
      ? container
      : container.querySelector("pre code, pre, code");
    return source?.innerText.replace(/\n$/, "") || "";
  };

  const addCodeCopyButtons = () => {
    const containers = [
      ...document.querySelectorAll(".highlight, div.fragment, .example-wrap"),
      ...[...document.querySelectorAll("pre")].filter(
        (pre) => !pre.closest(".highlight, div.fragment, .example-wrap"),
      ),
    ];
    containers.forEach((sourceContainer) => {
      let container = sourceContainer;
      if (sourceContainer.matches("pre")) {
        container = document.createElement("div");
        sourceContainer.before(container);
        container.append(sourceContainer);
      }
      if (container.classList.contains("dockle-code-block")) {
        return;
      }
      container.classList.add("dockle-code-block");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "dockle-copy-button";
      button.setAttribute("aria-label", "Copy code");
      button.title = "Copy code";
      button.innerHTML = '<i data-lucide="copy" aria-hidden="true"></i>';
      button.addEventListener("click", async () => {
        try {
          await copyText(codeText(container));
          const icon = button.querySelector("[data-lucide]");
          icon.dataset.lucide = "check";
          renderIcon(icon);
          button.setAttribute("aria-label", "Code copied");
          button.title = "Code copied";
          window.setTimeout(() => {
            const currentIcon = button.querySelector("[data-lucide]");
            currentIcon.dataset.lucide = "copy";
            renderIcon(currentIcon);
            button.setAttribute("aria-label", "Copy code");
            button.title = "Copy code";
          }, 1600);
        } catch {
          button.setAttribute("aria-label", "Unable to copy code");
          button.title = "Unable to copy code";
        }
      });
      container.append(button);
    });
  };

  const replaceRustdocIcons = () => {
    if (root.dataset.dockleFramework !== "rustdoc") {
      return;
    }
    const controls = [
      ["#copy-path", "copy"],
      [".settings-menu > a", "settings"],
      [".help-menu > a", "circle-help"],
      ["button#toggle-all-docs", "chevrons-down"],
    ];
    controls.forEach(([selector, iconName]) => {
      document.querySelectorAll(selector).forEach((control) => {
        if (control.querySelector(":scope > .dockle-rustdoc-icon")) {
          return;
        }
        const icon = document.createElement("i");
        icon.className = "dockle-rustdoc-icon";
        icon.dataset.lucide = iconName;
        icon.setAttribute("aria-hidden", "true");
        control.prepend(icon);
        if (control.id === "copy-path") {
          const updateCopyPathIcon = () => {
            icon.dataset.lucide = control.classList.contains("clicked")
              ? "check"
              : "copy";
            renderIcon(icon);
          };
          new MutationObserver(updateCopyPathIcon).observe(control, {
            attributeFilter: ["class"],
            attributes: true,
          });
        }
      });
    });
  };

  const addHeadingPermalinks = () => {
    const contentSelectors = {
      doxygen: "#doc-content .contents",
      jsdoc: "#main",
      mkdocs: ".dockle-article",
      rustdoc: "#main-content",
      sphinx: ".dockle-article",
    };
    const content = document.querySelector(
      contentSelectors[root.dataset.dockleFramework],
    );
    if (!content) {
      return;
    }
    const uniqueHeadingId = (title) => {
      const base = title
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLocaleLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "") || "section";
      let candidate = base;
      let suffix = 2;
      while (document.getElementById(candidate)) {
        candidate = `${base}-${suffix}`;
        suffix += 1;
      }
      return candidate;
    };
    content.querySelectorAll("h1, h2, h3, h4, h5, h6").forEach((heading) => {
      if (!heading.getClientRects().length
          || heading.querySelector(":scope > .dockle-heading-anchor")) {
        return;
      }
      const nativeLink = heading.querySelector(
        ":scope > .headerlink, :scope > .doc-anchor",
      );
      const nativeTarget = heading.querySelector(":scope > .anchor[id]");
      const nativeHref = nativeLink?.getAttribute("href") || "";
      let target = heading.id || nativeTarget?.id || "";
      if (!target && nativeHref.startsWith("#") && nativeHref.length > 1) {
        target = nativeHref.slice(1);
      }
      const title = heading.cloneNode(true);
      title.querySelectorAll(
        ".anchor, .doc-anchor, .headerlink, .dockle-heading-anchor, button",
      ).forEach((element) => element.remove());
      const headingTitle = title.textContent.trim();
      if (!headingTitle) {
        return;
      }
      if (!target) {
        target = uniqueHeadingId(headingTitle);
        heading.id = target;
      }
      heading.querySelectorAll(":scope > .headerlink, :scope > .doc-anchor")
        .forEach((anchor) => anchor.remove());
      const link = document.createElement("a");
      link.className = "dockle-heading-anchor";
      link.href = `#${target}`;
      link.title = "Link to this heading";
      link.setAttribute("aria-label", `Link to ${headingTitle}`);
      link.innerHTML = '<i data-lucide="pilcrow" aria-hidden="true"></i>';
      heading.append(link);
    });
  };

  const placeBuiltWithFooter = () => {
    const footer = document.querySelector("[data-dockle-built-with]");
    const destinations = {
      doxygen: "#doc-content .contents",
      jsdoc: "#main",
      mkdocs: ".dockle-article",
      rustdoc: "#main-content",
      sphinx: ".dockle-article",
    };
    const selector = destinations[root.dataset.dockleFramework];
    const destination = selector ? document.querySelector(selector) : null;
    if (footer && destination && !destination.contains(footer)) {
      destination.append(footer);
    }
  };

  const createCompatibilityPageNav = (framework) => {
    const pageNav = document.createElement("aside");
    if (framework === "doxygen") {
      pageNav.id = "page-nav";
      document.querySelector("#container")?.append(pageNav);
      return pageNav;
    }
    pageNav.className = "dockle-on-this-page dockle-compat-toc";
    pageNav.setAttribute("aria-label", "On this page");
    document.body.append(pageNav);
    return pageNav;
  };

  const compatibilityPageNav = (framework) => {
    const selector = framework === "doxygen"
      ? "#page-nav"
      : ".dockle-compat-toc";
    return document.querySelector(selector)
      || createCompatibilityPageNav(framework);
  };

  const compatibilityHeadings = (framework) => {
    const headingSelectors = {
      doxygen: "#doc-content .contents h1.doxsection, "
        + "#doc-content .contents h2.groupheader, "
        + "#doc-content .contents h2.memtitle, "
        + "#doc-content .contents h3",
      jsdoc: "#main article h2, #main article h3",
      rustdoc: "#main-content .docblock h2, "
        + "#main-content .docblock h3, "
        + "#main-content .docblock h4, "
        + "#main-content > h2.section-header",
    };
    const headings = [...document.querySelectorAll(headingSelectors[framework])]
      .filter((heading) => getComputedStyle(heading).display !== "none");
    if (headings.length) {
      return headings;
    }
    const fallbackSelectors = {
      doxygen: "#doc-content div.header .title",
      jsdoc: "#main h1",
      rustdoc: "#main-content h1",
    };
    const heading = document.querySelector(fallbackSelectors[framework]);
    if (!heading) {
      return headings;
    }
    heading.id ||= "dockle-page-start";
    return [heading];
  };

  const pageTocContents = (pageNav, framework) => {
    let contents = framework === "doxygen"
      ? pageNav.querySelector("#page-nav-contents")
      : pageNav;
    if (contents) {
      return contents;
    }
    contents = document.createElement("div");
    contents.id = "page-nav-contents";
    pageNav.append(contents);
    return contents;
  };

  const addPageTocTitle = (contents) => {
    if (contents.querySelector(".dockle-toc-title")) {
      return;
    }
    const title = document.createElement("strong");
    title.className = "dockle-toc-title";
    title.textContent = "On this page";
    contents.prepend(title);
  };

  const populatePageToc = (contents, framework) => {
    if (contents.querySelector("a")) {
      return;
    }
    const headings = compatibilityHeadings(framework);
    const list = document.createElement("ul");
    list.className = "page-outline";
    const levels = headings.map((heading) => Number(heading.tagName.slice(1)));
    const baseLevel = Math.min(...levels);
    headings.forEach((heading, index) => {
      const anchor = heading.querySelector(".anchor[id]");
      heading.id ||= anchor?.id || `dockle-section-${index + 1}`;
      const item = document.createElement("li");
      const depth = Math.min(Number(heading.tagName.slice(1)) - baseLevel, 2);
      item.classList.add(`dockle-toc-depth-${depth}`);
      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      const title = heading.cloneNode(true);
      title.querySelectorAll(
        ".anchor, .doc-anchor, .headerlink, .dockle-heading-anchor",
      ).forEach((anchor) => anchor.remove());
      link.textContent = title.textContent.trim();
      item.append(link);
      list.append(item);
    });
    contents.append(list);
  };

  const ensureCompatibilityPageToc = () => {
    const framework = root.dataset.dockleFramework;
    if (!["doxygen", "jsdoc", "rustdoc"].includes(framework)) {
      return;
    }
    const pageNav = compatibilityPageNav(framework);
    const usesNativePageToc = framework === "doxygen"
      && pageNav.classList.contains("page-nav-panel");
    pageNav.querySelectorAll(".dockle-heading-anchor").forEach(
      (anchor) => anchor.remove(),
    );
    pageNav.classList.add("dockle-page-toc");
    const contents = pageTocContents(pageNav, framework);
    addPageTocTitle(contents);
    populatePageToc(contents, framework);
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
  addCodeCopyButtons();
  replaceRustdocIcons();
  placeBuiltWithFooter();
  if (root.dataset.dockleFramework === "doxygen") {
    window.addEventListener("load", ensureCompatibilityPageToc);
  } else {
    ensureCompatibilityPageToc();
  }
  addHeadingPermalinks();
  renderIcons();
  updateThemeButtons();
})();
