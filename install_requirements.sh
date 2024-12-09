#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install a package
install_package() {
    PACKAGE=$1
    if command_exists apt; then
        sudo apt update && sudo apt install -y "$PACKAGE"
    elif command_exists yum; then
        sudo yum install -y "$PACKAGE"
    elif command_exists pacman; then
        sudo pacman -S --noconfirm "$PACKAGE"
    else
        echo "Unsupported package manager. Please install $PACKAGE manually."
        exit 1
    fi
}

# Packages to check and their corresponding installer packages
declare -A PACKAGE_MAP
PACKAGE_MAP=(
    ["ifconfig"]="net-tools"
    ["dnsmasq"]="dnsmasq"
    ["hostapd"]="hostapd"
    ["iptables"]="iptables"
    ["pkill"]="procps"
    ["awk"]="gawk"
    ["grep"]="grep"
)

# Iterate over the packages and install missing ones
for COMMAND in "${!PACKAGE_MAP[@]}"; do
    echo "Checking $COMMAND..."
    if ! command_exists "$COMMAND"; then
        echo "$COMMAND is not installed. Installing ${PACKAGE_MAP[$COMMAND]}..."
        install_package "${PACKAGE_MAP[$COMMAND]}"
    else
        echo "$COMMAND is already installed."
    fi
done

echo "All required packages are installed!"
