# Captive Portal

A captive portal is a web page that users on a public network must interact with before gaining access to the internet. This project sets up a captive portal with minimal configuration, requiring only the network name (SSID) and a port number.

#F eatures

* Automatically configures the Wi-Fi hotspot.
* Allows customization of the SSID and port number.
* Simplifies the process with an automated setup script.

# Requirements

A Wi-Fi module that supports the nl80211 driver.
The Wi-Fi module must support master mode (Access Point mode).

# Installation

Clone the repository:
git clone https://github.com/your-repository/captive-portal.git
cd captive-portal
Make the installation script executable:
chmod +x install_requirements.sh
Run the installation script to install the required dependencies:
./install_requirements.sh

# Usage

Run the setup script with sudo:
sudo python hotspotSetup.py
During the setup process, provide:
The SSID (Wi-Fi network name).
The port number for the captive portal.

# Additional Notes

Ensure your Wi-Fi module is compatible with nl80211 and can operate in master mode.
Use the command below to check Wi-Fi driver compatibility:
iw list | grep -A 10 "Supported interface modes"
If you encounter issues, verify that the dependencies (hostapd, dnsmasq, etc.) are properly installed using:
which <command>

# Contributing

Contributions are welcome! Feel free to fork the repository, create a feature branch, and submit a pull request.

License

This project is licensed under the MIT License.
