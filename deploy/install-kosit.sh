#!/usr/bin/env bash
# Install pinned KoSIT Validator and XRechnung scenarios on the production host.
set -euo pipefail

readonly INSTALL_ROOT="${INSTALL_ROOT:-/opt/kosit}"
readonly VALIDATOR_VERSION="1.6.3"
readonly CONFIG_VERSION="2026-01-31"
readonly RELEASE_NAME="validator-${VALIDATOR_VERSION}_xrechnung-${CONFIG_VERSION}"
readonly RELEASE_DIR="${INSTALL_ROOT}/releases/${RELEASE_NAME}"
readonly VALIDATOR_ARCHIVE="validator-${VALIDATOR_VERSION}-standalone.jar"
readonly CONFIG_ARCHIVE="xrechnung-3.0.2-validator-configuration-${CONFIG_VERSION}.zip"
readonly VALIDATOR_URL="https://github.com/itplr-kosit/validator/releases/download/v${VALIDATOR_VERSION}/${VALIDATOR_ARCHIVE}"
readonly CONFIG_URL="https://github.com/itplr-kosit/validator-configuration-xrechnung/releases/download/v${CONFIG_VERSION}/${CONFIG_ARCHIVE}"
readonly VALIDATOR_SHA256="799e64befca97d4080e03608c80b85dd5a5ecc5f4ae4f35d1116ec2855b9a7c9"
readonly CONFIG_SHA256="6a5a5911a421b25fbc423f62f93f894df7b236f5d73ca4f84bb222a945082704"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root to install KoSIT under ${INSTALL_ROOT}." >&2
  exit 1
fi

for command_name in curl java sha256sum unzip; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing command: ${command_name}" >&2
    echo "On Debian/Ubuntu install: openjdk-17-jre-headless curl unzip ca-certificates" >&2
    exit 1
  fi
done

java -version
install -d -m 0750 -o root -g www-data "${INSTALL_ROOT}/releases"

print_environment() {
  echo "Add or update these values in /opt/eInvoice/backend/.env:"
  echo "KOSIT_JAVA_BIN=/usr/bin/java"
  echo "KOSIT_VALIDATOR_JAR=${INSTALL_ROOT}/current/validator.jar"
  echo "KOSIT_SCENARIOS_XML=${INSTALL_ROOT}/current/scenarios.xml"
  echo "KOSIT_REQUIRED=true"
}

if [[ -e "${RELEASE_DIR}" ]]; then
  echo "==> Pinned release already exists: ${RELEASE_DIR}"
  echo "${VALIDATOR_SHA256}  ${RELEASE_DIR}/validator.jar" | sha256sum --check -
  if [[ ! -f "${RELEASE_DIR}/scenarios.xml" ]]; then
    echo "Existing release does not contain scenarios.xml." >&2
    exit 1
  fi
  ln -sfnT "${RELEASE_DIR}" "${INSTALL_ROOT}/current"
  chown -h root:www-data "${INSTALL_ROOT}/current"
  print_environment
  exit 0
fi

STAGING_DIR="$(mktemp -d "${INSTALL_ROOT}/.install.XXXXXX")"
readonly STAGING_DIR
cleanup() {
  rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

echo "==> Download KoSIT Validator ${VALIDATOR_VERSION}"
curl --fail --location --proto '=https' --tlsv1.2 \
  "${VALIDATOR_URL}" --output "${STAGING_DIR}/${VALIDATOR_ARCHIVE}"

echo "==> Download XRechnung configuration ${CONFIG_VERSION}"
curl --fail --location --proto '=https' --tlsv1.2 \
  "${CONFIG_URL}" --output "${STAGING_DIR}/${CONFIG_ARCHIVE}"

echo "${VALIDATOR_SHA256}  ${STAGING_DIR}/${VALIDATOR_ARCHIVE}" | sha256sum --check -
echo "${CONFIG_SHA256}  ${STAGING_DIR}/${CONFIG_ARCHIVE}" | sha256sum --check -

unzip -q "${STAGING_DIR}/${CONFIG_ARCHIVE}" -d "${STAGING_DIR}/configuration"
install -m 0640 -o root -g www-data \
  "${STAGING_DIR}/${VALIDATOR_ARCHIVE}" "${STAGING_DIR}/configuration/validator.jar"
rm -f "${STAGING_DIR}/${VALIDATOR_ARCHIVE}" "${STAGING_DIR}/${CONFIG_ARCHIVE}"

if [[ ! -f "${STAGING_DIR}/configuration/scenarios.xml" ]]; then
  echo "Downloaded configuration does not contain scenarios.xml." >&2
  exit 1
fi

chown -R root:www-data "${STAGING_DIR}/configuration"
find "${STAGING_DIR}/configuration" -type d -exec chmod 0750 {} +
find "${STAGING_DIR}/configuration" -type f -exec chmod 0640 {} +
mv "${STAGING_DIR}/configuration" "${RELEASE_DIR}"

ln -sfnT "${RELEASE_DIR}" "${INSTALL_ROOT}/current"
chown -h root:www-data "${INSTALL_ROOT}/current"

echo "==> KoSIT installed"
print_environment
