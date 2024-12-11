import subprocess
import re
import time
import signal
import sys
import threading

port = ""
DhcpPort = ""
stoping = False
stopingHotsport = False

redText = "\033[31m{}. \003"
EndText = "\033[37mPress Ctrl+C to exit. \003"

def list_interface():
    # Run the full command in a shell, since we're using pipes and multiple commands
    command = "nmcli device status | grep -e 'wifi' -e 'wl' | awk 'NR==1 {print $1}'"
    
    # subprocess.run to execute the command in the shell
    res = subprocess.run(command, shell=True, capture_output=True, check=True, text=True)
    
    interface=res.stdout.strip()

    return interface

def handle_exit_signal(signal, frame):
    global startHotsport_thread
    global stoping
    global server_thread
    global stopingHotsport
    print("\n\033[32mProcess is ending. Cleaning up...\033")
    stopingHotsport = True
    stoping = True
    if server_thread and server_thread.is_alive():
        server_thread.join()
    stopHotsport()
    if startHotsport_thread and startHotsport_thread.is_alive():
        startHotsport_thread.join()
    downCreatedIpTable(port)
    downCreatedIpTable(DhcpPort)
    print("\033[32mProcess execution complited successfully\033")
    sys.exit(0)

def setUpIP(wifi):
    command = ["sudo","ifconfig",wifi,"192.168.28.1/24"]
    result = subprocess.run(command,text=True)
    if not result.stdout:
        print(("IP setup for {}".format(wifi)))
    else:
        print(redText.format("IP setup not done error : \n{}".format(result.stdout)))
        print(EndText)

def setUpIptables(wifi,hdcpPort):
    global DhcpPort
    DhcpPort = hdcpPort
    command = ["sudo", "iptables", "-t", "nat", "-A", "PREROUTING",
    "-i", wifi, "-p", "tcp", "--dport", "80",
    "-j", "DNAT", "--to-destination", f"192.168.28.1:{port}"]
    command_DhcpPortForwardeing1=f"sudo iptables -t nat -A PREROUTING -p tcp --dport 53 -j REDIRECT --to-port {hdcpPort}"
    command_DhcpPortForwardeing2=f"sudo iptables -t nat -A PREROUTING -p udp --dport 53 -j REDIRECT --to-port {hdcpPort}"
    try:
        subprocess.run(command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(command_DhcpPortForwardeing1,shell=True)
        subprocess.run(command_DhcpPortForwardeing2,shell=True)
    except subprocess.CalledProcessError as e:
        print(redText.format("An error occurred : \n",e))
        print(EndText)

def indexOfIpTable(result,port):
    key = port
    targetNumber = []
    for line in enumerate(result.stdout.splitlines()):
        if line[1].find(key)!=-1:
            targetNumber.append((re.search(r'\d+',line[1])).group())
    return targetNumber

def downCreatedIpTable(port):
    command = ["sudo","iptables","-t","nat","-L","--line-numbers"]
    result = subprocess.run(command,capture_output=True, text=True)
    targetNumbers = indexOfIpTable(result,port)
    if targetNumbers:
        count = 0
        for targetNumber in targetNumbers:
            targetNumber = str(int(targetNumber)-count)
            command = ["sudo","iptables","-t","nat","-D","PREROUTING",targetNumber]
            subprocess.run(command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            count += 1
    targetNumbers = indexOfIpTable(result,port)
    if not targetNumbers:
        print("Some error happend") 

def stopHotsport():
    hostapdStopCommand = ["sudo","pkill","hostapd"]
    dnsmasqGetProcessIdCommand = "ps aux | grep dnsmasq"
    subprocess.run(hostapdStopCommand,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    result = subprocess.run(dnsmasqGetProcessIdCommand,capture_output=True, text=True, shell=True)
    output = result.stdout.splitlines()
    id = None
    for line in output:
        if line.find("dhcpConfig.conf") != -1:
            id = (re.search(r'\d+',line)).group()
    if id:
        dnsmasqKillCommand = "sudo kill {}".format(id)
        subprocess.run(dnsmasqKillCommand,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)
    

def startHotsport():
    hostapdStartCommand = ["sudo","hostapd","hostapd.conf"]
    dnsmasqStartCommand = ["sudo","dnsmasq","-C","dhcpConfig.conf"]
    dns = subprocess.run(dnsmasqStartCommand,text=True)
    if dns.stdout:
        print(redText.format("An Error occurred in dns server"))
        print(EndText)
    try:
        process = subprocess.Popen(hostapdStartCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # count = 0
        while not stopingHotsport:
            time.sleep(1)
            line = process.stdout.readlines()
            if process.poll() is not None and not stopingHotsport:
                print(redText.format("An error occurred when creating hotsport"))
                print(EndText)
                break
            if line and line.strip() == "handle_probe_req: send failed":
                print("restart agaun")
                print(redText.format("An error occurred when creating hotsport"))
                print(EndText)
                break
            # if count > 5:
            #     print("process restarting")
            #     process.terminate()
            #     process = subprocess.Popen(hostapdStartCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #     time.sleep(1)
            #     count = 0
    except:
        print("")

def startServer(portValue):
    global port
    port = portValue
    python_executable = sys.executable
    command = [python_executable,"app.py",portValue]
    process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while not stoping:
        continue
    process.terminate()

def editConfigFile(new_value,filepath,key):
    with open(filepath, "r") as file:
        lines = file.readlines()
    updated_lines = [
        f"{key}{new_value}\n" if line.strip().startswith(key) else line
        for line in lines
    ]
    with open(filepath, "w") as file:
        file.writelines(updated_lines)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit_signal)
    defaultWifiName = "WifiUpdate"
    defaultSerevrPort = "9090"
    defaultdnsPort = "9292"
    wifi = list_interface()
    editConfigFile(wifi,'dhcpConfig.conf',"interface=")
    editConfigFile(wifi,'hostapd.conf',"interface=")
    userDifinedPort = input(f"give a port number for server default({defaultSerevrPort}): ") or defaultSerevrPort
    userDifinedDnspPort = input(f"give a port number for dns default({defaultdnsPort}): ") or defaultdnsPort
    wifiName = input(f"Give a name for wifi default({defaultWifiName}): ") or defaultWifiName
    print("Using wifi interface",wifi)
    editConfigFile(wifiName,'hostapd.conf',"ssid=")
    editConfigFile(userDifinedDnspPort,'dhcpConfig.conf',"port=")
    server_thread = threading.Thread(target=startServer,args=(userDifinedPort,))
    server_thread.start()

    setUpIP(wifi)
    setUpIptables(wifi,userDifinedDnspPort)

    startHotsport_thread = threading.Thread(target=startHotsport)
    startHotsport_thread.start()
    
    print("Press Ctrl+C to exit.")
    while True:
        pass