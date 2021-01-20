#! /usr/bin/env bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../.. && pwd)"
cd "${PROJECT_ROOT}"

# Generate
rm -r generated >/dev/null 2>&1 || true
./scripts/generate.sh -p client -n debugtest.client -i ./scripts/dev/test_swagger.json -o testclient

