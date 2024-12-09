# **Captive Portal**

A **captive portal** is a web page that users on a public network must interact with before gaining access to the internet. This project sets up a **captive portal** with minimal configuration, requiring only the network name (SSID) and a port number.

---

## **Features**
- Automatically configures the Wi-Fi hotspot.
- Allows customization of the SSID and port number.
- Simplifies the process with an automated setup script.

---

## **Requirements**
- A Wi-Fi module that:
  - Supports the `nl80211` driver.
  - Can operate in **master mode** (Access Point mode).

---

## **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/captive-portal.git
   cd captive-portal

2. Make the installation script executable:
   ```bash
    chmod +x install_requirements.sh
3. Run the installation script to install the required dependencies:
   ```bash
    ./install_requirements.sh

# Usage

1. Run the setup script with sudo:
   ```bash
    sudo python hotspotSetup.py
2. During the setup process, provide:
- The SSID (Wi-Fi network name).
- The port number for the captive portal.

# Troubleshooting

- Ensure your Wi-Fi module is compatible with nl80211 and can operate in master mode.
- Use the command below to check Wi-Fi driver compatibility:
  ```bash
  iw list | grep -A 10 "Supported interface modes"
- If you encounter issues, verify that the dependencies (hostapd, dnsmasq, etc.) are properly installed using:
  ```bash
  which <command>

# Contributing

Contributions are welcome! Feel free to 
- fork the repository
- create a feature branch
- submit a pull request.

License

This project is licensed under the MIT License.
