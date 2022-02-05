import serial
import os
from serial.serialutil import SerialException
from serial.serialwin32 import Serial
import time

def setup_com_ports(recv_dev :Serial, send_dev :Serial):
    send_dev.baudrate = 1152000
    send_dev.port = input("Sender Device COM port?\n")
    send_dev.timeout = 3
    try:
        send_dev.open()
    except SerialException:
        print("Could not open the sender serial console")
        send_dev.close()
        return -1

    recv_dev.baudrate = 1152000
    recv_dev.port = input("Receiver Device COM port?\n")
    recv_dev.timeout = 3
    try:
        recv_dev.open()
    except SerialException:
        print("Could not open the receiver serial console")
        recv_dev.close()
        return -1
    
    return 0

def write_coding_rate(recv_dev :Serial, send_dev :Serial, coding_rate):
    if(coding_rate == "1"):
        recv_dev.write(b'1');
        send_dev.write(b'1');
    elif(coding_rate == "2"):
        recv_dev.write(b'2');
        send_dev.write(b'2');
    elif(coding_rate == "3"):
        recv_dev.write(b'3');
        send_dev.write(b'3');
    elif(coding_rate == "4"):
        recv_dev.write(b'4');
        send_dev.write(b'4');

def write_spreading_factor(recv_dev :Serial, send_dev:Serial, spreading_factor):
    if(spreading_factor == "6"):
        recv_dev.write(b'6');
        send_dev.write(b'6');
    elif(spreading_factor == "7"):
        recv_dev.write(b'7');
        send_dev.write(b'7');
    elif(spreading_factor == "8"):
        recv_dev.write(b'8');
        send_dev.write(b'8');
    elif(spreading_factor == "9"):
        recv_dev.write(b'9');
        send_dev.write(b'9');
    elif(spreading_factor == "10"):
        recv_dev.write(b'10');
        send_dev.write(b'10');
    elif(spreading_factor == "11"):
        recv_dev.write(b'11');
        send_dev.write(b'11');
    elif(spreading_factor == "12"):
        recv_dev.write(b'12');
        send_dev.write(b'12');
        

def main():
    sender = serial.Serial()
    receiver = serial.Serial()

    while(True):
        if(setup_com_ports(receiver, sender) != 0):
            continue
        
        while(True):
            if(input("Run new test? (y | n) ") == "y"):
                coding_rate = input("Coding rate: 1, 2, 3, 4? ")
                spreading_factor = input("Spreading factor: 6, 7, 8, 9, 10, 11, 12? ");
                packet_number = input("Number of packets per test? ")

                print("Receiver:");
                print("---------");
                while(receiver.inWaiting()):
                    for line in receiver.readline().split(b'\r\n'):
                        if(line == b''):
                            continue
                        print("\t {}".format(line))
                    
                print("Sender:");
                print("---------")
                while(sender.inWaiting()):
                    for line in sender.readline().split(b'\r\n'):
                        if(line == b''):
                            continue
                        print("\t {}".format(line))

                receiver.write(b'r')
                sender.write(b'r')
                time.sleep(1);
                write_coding_rate(receiver, sender, coding_rate)
                time.sleep(1);
                write_spreading_factor(receiver, sender, spreading_factor)
                time.sleep(1);

                attenuations = ["0", "60", "70", "90", "100", "110", "120", "130", "140", "145", "146", "147", "148", "149", "150"]
                for att in attenuations:
                    input("Set the att to {}".format(att));
                    test_file_name = "data_{}_{}_{}_{}.txt".format("500kHz", coding_rate, spreading_factor, att)
                    test_file = open(test_file_name, "w");

                    start_time = time.time();
                    print("Receiver:");
                    print("---------");
                    while(receiver.inWaiting()):
                        for line in receiver.readline().split(b'\r\n'):
                            if(line == b''):
                                continue
                            print("\t {}".format(line))
                        
                    print("Sender:");
                    print("---------")
                    while(sender.inWaiting()):
                        for line in sender.readline().split(b'\r\n'):
                            if(line == b''):
                                continue
                            print("\t {}".format(line))

                    """
                    Run through the tests
                    """

                    for i in range(0, int(packet_number)+1):
                        sender.flushInput();
                        sender.write(b'\n');
                        sender_data = sender.readline()
                        test_file.write("{}.a: ".format(i))
                        test_file.write(sender_data.decode('utf-8').rstrip());
                        test_file.write('\n');

                        rec_data = receiver.readline();
                        test_file.write("{}.b: ".format(i))
                        test_file.write(rec_data.decode('utf-8').rstrip());
                        test_file.write('\n');
                    
                    print("Test elapse time (s): {}".format(time.time() - start_time));
                    test_file.close();
            else:
                exit();

if __name__ == "__main__":
    main()