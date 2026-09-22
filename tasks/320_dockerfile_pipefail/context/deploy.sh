#!/bin/sh
# Installs or upgrades one release from the chart mounted at /chart.
set -eu
helm upgrade --install "$RELEASE" /chart --namespace "$NAMESPACE" --wait
