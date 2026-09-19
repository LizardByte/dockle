#!/usr/bin/env bash
set -euo pipefail

dockle_dir="$(cd -- "${DOCKLE_DIR:-$(dirname -- "${BASH_SOURCE[0]}")}" && pwd -P)"
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

uv_run=("${environment_run[@]}" uv)
"${uv_run[@]}" sync --project "${dockle_dir}" --locked --all-extras --no-dev
dockle_run=(
  "${uv_run[@]}" run --project "${dockle_dir}" --locked --all-extras --no-dev --no-sync
)

if [[ -f docs/requirements.txt ]]; then
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
