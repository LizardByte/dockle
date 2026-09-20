#!/usr/bin/env bash
set -euo pipefail

dockle_dir="$(cd -- "${DOCKLE_DIR:-$(dirname -- "${BASH_SOURCE[0]}")}" && pwd -P)"
project_dir="$(pwd -P)"
environment_name="${READTHEDOCS_VERSION:-dockle-docs}"
environment_file="${dockle_dir}/environment.yml"
uses_doxygen="$(
  python -c \
    'import tomllib; config = tomllib.load(open("dockle.toml", "rb")); print(any(t.get("framework") == "doxygen" for t in config["targets"]))'
)"

if [[ "${uses_doxygen}" == "True" ]]; then
  echo "Creating the Dockle documentation environment from ${environment_file}"
  conda env create --quiet --name "${environment_name}" --file "${environment_file}"
  environment_run=(conda run --no-capture-output --name "${environment_name}")
else
  echo "Using the Read the Docs Python environment; this project has no Doxygen target"
  environment_run=()
fi

npm --prefix "${dockle_dir}" ci --ignore-scripts
npm --prefix "${dockle_dir}" run build

uv_run=("${environment_run[@]}" python -m uv)
"${uv_run[@]}" sync --project "${dockle_dir}" --locked --all-extras --no-dev
dockle_run=(
  "${uv_run[@]}" run --project "${dockle_dir}" --locked --all-extras --no-dev --no-sync
)

uses_docs_group="$(
  python -c \
    'import pathlib, tomllib; path = pathlib.Path("pyproject.toml"); print(path.is_file() and "docs" in tomllib.load(path.open("rb")).get("dependency-groups", {}))'
)"

if [[ "${uses_docs_group}" == "True" ]]; then
  echo "Installing the locked project documentation dependency group"
  docs_requirements="$(mktemp)"
  trap 'rm -f "${docs_requirements}"' EXIT
  "${uv_run[@]}" export \
    --quiet \
    --project "${project_dir}" \
    --locked \
    --only-group docs \
    --no-emit-project \
    --format requirements.txt \
    --output-file "${docs_requirements}"
  "${uv_run[@]}" pip install \
    --python "${dockle_dir}/.venv/bin/python" \
    --requirement "${docs_requirements}"
  rm -f "${docs_requirements}"
  trap - EXIT
elif [[ -f docs/requirements.txt ]]; then
  "${uv_run[@]}" pip install \
    --python "${dockle_dir}/.venv/bin/python" \
    --requirement docs/requirements.txt
fi

if [[ -f readthedocs_pre_build.sh ]]; then
  chmod +x readthedocs_pre_build.sh
  ./readthedocs_pre_build.sh
fi

"${dockle_run[@]}" python -m dockle check
"${dockle_run[@]}" python -m dockle build

if [[ -f readthedocs_post_build.sh ]]; then
  chmod +x readthedocs_post_build.sh
  ./readthedocs_post_build.sh
fi

mkdir -p "${READTHEDOCS_OUTPUT}html/"
cp -r _site/. "${READTHEDOCS_OUTPUT}html/"
