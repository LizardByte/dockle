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
  python_run=(conda run --no-capture-output --name "${environment_name}" python)
else
  echo "Using the Read the Docs Python environment; this project has no Doxygen target"
  python_run=(python)
fi

if [[ "${project_dir}" == "${dockle_dir}" ]]; then
  npm ci --ignore-scripts
  npm run build
  "${python_run[@]}" -m pip install '.[all]'
else
  "${python_run[@]}" -m pip install --requirement "${dockle_dir}/requirements-readthedocs.txt"
  export PYTHONPATH="${dockle_dir}/src${PYTHONPATH:+:${PYTHONPATH}}"
fi

if [[ -f docs/requirements.txt ]]; then
  "${python_run[@]}" -m pip install --requirement docs/requirements.txt
fi

if [[ -f readthedocs_pre_build.sh ]]; then
  chmod +x readthedocs_pre_build.sh
  ./readthedocs_pre_build.sh
fi

"${python_run[@]}" -m dockle check
"${python_run[@]}" -m dockle build

if [[ -f readthedocs_post_build.sh ]]; then
  chmod +x readthedocs_post_build.sh
  ./readthedocs_post_build.sh
fi

mkdir -p "${READTHEDOCS_OUTPUT}html/"
cp -r _site/. "${READTHEDOCS_OUTPUT}html/"
