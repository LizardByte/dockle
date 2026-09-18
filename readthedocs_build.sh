#!/usr/bin/env bash
set -euo pipefail

dockle_dir="$(cd -- "${DOCKLE_DIR:-$(dirname -- "${BASH_SOURCE[0]}")}" && pwd -P)"
project_dir="$(pwd -P)"
environment_name="${READTHEDOCS_VERSION:-dockle-docs}"
environment_file="${dockle_dir}/environment.yml"
conda_run=(conda run --no-capture-output --name "${environment_name}")

echo "Creating the Dockle documentation environment from ${environment_file}"
conda env create --quiet --name "${environment_name}" --file "${environment_file}"

if [[ "${project_dir}" == "${dockle_dir}" ]]; then
  npm ci --ignore-scripts
  npm run build
  "${conda_run[@]}" python -m pip install '.[all]'
else
  "${conda_run[@]}" python -m pip install --requirement "${dockle_dir}/requirements-readthedocs.txt"
  export PYTHONPATH="${dockle_dir}/src${PYTHONPATH:+:${PYTHONPATH}}"
fi

if [[ -f docs/requirements.txt ]]; then
  "${conda_run[@]}" python -m pip install --requirement docs/requirements.txt
fi

if [[ -f readthedocs_pre_build.sh ]]; then
  chmod +x readthedocs_pre_build.sh
  ./readthedocs_pre_build.sh
fi

"${conda_run[@]}" python -m dockle check
"${conda_run[@]}" python -m dockle build

if [[ -f readthedocs_post_build.sh ]]; then
  chmod +x readthedocs_post_build.sh
  ./readthedocs_post_build.sh
fi

mkdir -p "${READTHEDOCS_OUTPUT}html/"
cp -r _site/. "${READTHEDOCS_OUTPUT}html/"
