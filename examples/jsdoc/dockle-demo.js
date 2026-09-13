/**
 * Utilities for describing a documentation build.
 * @module dockle-demo
 */

/** A documentation target consumed by Dockle. */
export class DocumentationTarget {
  /**
   * Create a target.
   * @param {string} name Stable name used for the output directory.
   * @param {string} framework Upstream documentation framework.
   */
  constructor(name, framework) {
    this.name = name;
    this.framework = framework;
  }

  /**
   * Return a human-readable summary.
   * @returns {string} Target and framework joined for display.
   */
  summary() {
    return `${this.name} (${this.framework})`;
  }
}

/**
 * Select targets matching a framework.
 * @param {DocumentationTarget[]} targets Candidate documentation targets.
 * @param {string} framework Framework to select.
 * @returns {DocumentationTarget[]} Matching targets in their original order.
 */
export function selectByFramework(targets, framework) {
  return targets.filter((target) => target.framework === framework);
}
