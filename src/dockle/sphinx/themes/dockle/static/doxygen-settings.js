/* global Cookie, dockleDoxygenNavigationPages */

(() => {
  if (typeof Cookie === 'undefined') return;

  // cookie.js resolves to the same documentation root from every nested page.
  const documentationRoot = new URL('.', document.currentScript.src);
  Cookie.cookie_namespace = `dockle_doxygen_${encodeURIComponent(documentationRoot.pathname)}_`;

  const navigationPages = new Set(dockleDoxygenNavigationPages);
  const readSetting = Cookie.readSetting;
  Cookie.readSetting = function (setting, defaultValue) {
    const value = readSetting.call(this, setting, defaultValue);
    if (setting === 'navpath' && value && !navigationPages.has(value.split('#')[0])) {
      // Doxygen's homepage fallback would otherwise reuse this invalid URL.
      this.eraseSetting(setting);
      return defaultValue;
    }
    return value;
  };

  const configureLayout = () => {
    // Dockle owns panel geometry; Doxygen still owns tree expansion and scrolling.
    // Discard only the inline dimensions that would override the responsive CSS.
    const panels = [
      ['side-nav', ['height', 'width']],
      ['nav-tree', ['height']],
      ['doc-content', ['height', 'margin-left']],
      ['page-nav', ['width']],
    ];
    for (const [id, properties] of panels) {
      const panel = document.getElementById(id);
      if (!panel) continue;
      const reset = () => {
        for (const property of properties) {
          if (panel.style.getPropertyValue(property)) {
            panel.style.removeProperty(property);
          }
        }
        // Native resizing also reserves a grid column for the page outline.
        const container = document.getElementById('container');
        if (id === 'page-nav' && panel.offsetWidth && container) {
          container.style.gridTemplateColumns = `auto ${panel.offsetWidth}px`;
        }
      };
      reset();
      new MutationObserver(reset).observe(panel, {
        attributes: true,
        attributeFilter: ['style'],
      });
    }
  };
  document.addEventListener('DOMContentLoaded', configureLayout, { once: true });
})();
