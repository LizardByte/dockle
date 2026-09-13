/** @file dockle_demo.hpp
 *  @brief A compact API used to review Dockle's Doxygen integration.
 */

#pragma once

#include <string_view>

namespace dockle::demo {

  /** Controls how aggressively documentation warnings are handled. */
  enum class warning_policy {
    /** Continue after reporting a warning. */
    report,
    /** Treat every warning as a failed build. */
    fail,
  };

  /** Describes a documentation target.
   *
   * A target combines a source directory with one upstream generator. Dockle
   * generates the native configuration just before executing the build.
   */
  class target {
  public:
    /** Construct a documentation target.
     * @param name Stable target name used for the output directory.
     * @param generator Upstream documentation generator.
     * @param policy Warning policy for the generator invocation.
     */
    constexpr target(
      std::string_view name,
      std::string_view generator,
      warning_policy policy
    ) noexcept:
        name_(name),
        generator_(generator),
        policy_(policy) {}

    /** Return the stable target name. */
    [[nodiscard]] constexpr std::string_view name() const noexcept {
      return name_;
    }

    /** Return the configured generator. */
    [[nodiscard]] constexpr std::string_view generator() const noexcept {
      return generator_;
    }

    /** Return the configured warning policy. */
    [[nodiscard]] constexpr warning_policy policy() const noexcept {
      return policy_;
    }

  private:
    std::string_view name_;  ///< Stable output name.
    std::string_view generator_;  ///< Native generator name.
    warning_policy policy_;  ///< Warning behavior.
  };

  /** Determine whether a target uses the requested generator.
   * @param value Target to inspect.
   * @param generator Generator name to compare.
   * @return `true` when the generator names match.
   */
  [[nodiscard]] constexpr bool uses(const target &value, std::string_view generator) noexcept {
    return value.generator() == generator;
  }

}  // namespace dockle::demo
