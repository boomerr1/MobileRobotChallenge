
import time
import socket
import sys
import picar_4wd as fc

## raspberry pi tcp setting
HOST_IP = "192.168.50.64"
HOST_PORT = 8888
print("Starting socket: TCP...")

## raspberry pi connect to PC
socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("TCP server listen @ %s:%d!" %(HOST_IP, HOST_PORT) )
host_addr = (HOST_IP, HOST_PORT)
socket_tcp.bind(host_addr)
socket_tcp.listen(3)
socket_con, (client_ip, client_port) = socket_tcp.accept()
print("Connection accepted from %s." %client_ip)

socket_con.send(str.encode("Welcome to RPi TCP server!"))

def turn_deg(direction, degrees=90):
        ninety_deg_time = 0.94*1.25
        if direction == 'r':
                fc.turn_right(10)
        else:
                fc.turn_left(10)
        time.sleep(degrees/90*ninety_deg_time)
        fc.stop()
        time.sleep(0.1)

red = fc.Pin('D0')
yellow = fc.Pin('D1')
green = fc.Pin('D2')

print("Receiving package...")
while True:
    ## receive message
    try:
        red.off()
        green.off()
        yellow.off()
        data=socket_con.recv(512)
        data = bytes.decode(data)
        if len(data)>0:
            print(f"Received:{data}\r")
            ## 
            if data == '11':
                for _ in range(5):
                        green.on()
                        time.sleep(0.1)
                        green.off()
                        time.sleep(0.1)
                        yellow.on()
                        time.sleep(0.1)
                        yellow.off()
                        red.on()
                        time.sleep(0.1)
                        red.off()
                        time.sleep(0.1)

            elif data == '00':
                red.on()
                time.sleep(1)
                red.off()
            elif data == '10':
                print('turn right')
                turn_deg('r')
                fc.forward(20)
                time.sleep(1)
                fc.stop()
                time.sleep(0.2)
                turn_deg('l')
            elif data == '01':
                print('turn left')
                turn_deg('l')
                fc.forward(20)
                time.sleep(1)
                fc.stop()
                time.sleep(0.2)
                turn_deg('r')
            elif data == '100':
                for _ in range(5):
                        yellow.on()
                        time.sleep(0.2)
                        yellow.off()
                        time.sleep(0.2)
            else:
                continue
    except Exception:
            red.off()
            green.off()
            yellow.off()
            socket_tcp.close()
            sys.exit(1)
