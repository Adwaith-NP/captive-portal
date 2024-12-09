import subprocess
import re
import time
import signal
import sys
import threading

port = ""
stoping = False
stopingHotsport = False

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
    print("\nProcess is ending. Cleaning up...")
    stoping = True
    server_thread.join()
    stopHotsport()
    stopingHotsport = True
    startHotsport_thread.join()
    downCreatedIpTable(port)
    sys.exit(0)

def setUpIP(wifi):
    command = ["sudo","ifconfig",wifi,"192.168.28.1/24"]
    result = subprocess.run(command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not result.stdout:
        print("IP setup for {}".format(wifi))
    else:
        print("IP setup not done error : \n{}".format(result.stdout))

def setUpIptables(wifi):
    command = ["sudo", "iptables", "-t", "nat", "-A", "PREROUTING",
    "-i", wifi, "-p", "tcp", "--dport", "80",
    "-j", "DNAT", "--to-destination", f"192.168.28.1:{port}"]
    try:
        subprocess.run(command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print("An error ocuarde : \n",e)

def indexOfIpTable(result,port):
    key = "192.168.28.1:"+port
    targetNumber = None
    for line in enumerate(result.stdout.splitlines()):
        if line[1].find(key)!=-1:
            targetNumber = (re.search(r'\d+',line[1])).group()
    return targetNumber

def downCreatedIpTable(port):
    command = ["sudo","iptables","-t","nat","-L","--line-numbers"]
    result = subprocess.run(command,capture_output=True, text=True)
    targetNumber = indexOfIpTable(result,port)
    if targetNumber:
        command = ["sudo","iptables","-t","nat","-D","PREROUTING",targetNumber]
        subprocess.run(command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    targetNumber = indexOfIpTable(result,port)
    if not targetNumber:
        print("Some error happend")
    else:
        print("Process complited")    

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
    subprocess.run(dnsmasqStartCommand,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process = subprocess.Popen(hostapdStartCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        count = 0
        while not stopingHotsport:
            line = process.stdout.readline()
            if line and line.strip() == "handle_probe_req: send failed":
                count+=1
            if count > 5:
                print("process restarting")
                process.terminate()
                process = subprocess.Popen(hostapdStartCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                time.sleep(1)
                count = 0
        print("Hotsport ended")
    except:
        print("An error")

def startServer(portValue):
    global port
    port = portValue
    python_executable = sys.executable
    command = [python_executable,"app.py",portValue]
    process = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while not stoping:
        continue
    process.terminate()
    print("Server stoped")

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
    wifi = list_interface()
    editConfigFile(wifi,'dhcpConfig.conf',"interface=")
    editConfigFile(wifi,'hostapd.conf',"interface=")
    userDifinedPort = input("give a port number : ")
    wifiName = input("Give a name for wifi : ")
    print(userDifinedPort,wifiName)
    if userDifinedPort == "" or wifiName == "":
        print("Try Again")
        exit(0)
    editConfigFile(wifiName,'hostapd.conf',"ssid=")
    server_thread = threading.Thread(target=startServer,args=(userDifinedPort,))
    server_thread.start()

    setUpIP(wifi)
    setUpIptables(wifi)

    startHotsport_thread = threading.Thread(target=startHotsport)
    startHotsport_thread.start()
    

    print("Press Ctrl+C to exit.")
    while True:
        pass