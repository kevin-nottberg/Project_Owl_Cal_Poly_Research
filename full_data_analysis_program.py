"""
    Create a dictionary that can then plot
    SF -> SNR dict
    SNR Dict -> [#Bits Sent, #Bits wrong, #BER, #Symbols Sent, #Symbols wrong, #SER, #Unanalyzable Packets]

    SF -> RSSI Dict
    RSSI Dict -> [#Bits Sent, #Bits wrong, #BER, #Symbols Sent, #Symbols wrong, #SER, #Unalayzable Packets]
"""

from audioop import avg
from cmath import isnan
from enum import unique
from functools import total_ordering
from hashlib import new
from posixpath import split
from tkinter import E
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import math

ignore_list = [];

class SF:
    def __init__(self, spreading_factor):
        self.spreading_factor = spreading_factor;
        self.snr_dict = {};
        self.rssi_dict = {};
        self.att_gain_dict = {};

        self.snr_ber_ser_x = [];
        self.snr_ber_y = [];
        self.snr_ber_trash_y = [];
        self.snr_ser_y = [];
        self.snr_trash_y = [];

        self.snr_ber_ser_x_sorted = [];
        self.snr_ber_y_sorted = [];
        self.snr_ber_trash_y_sorted = [];

        self.rssi_ber_ser_x = [];
        self.rssi_ber_y = [];
        self.rssi_ber_trash_y = [];
        self.rssi_ser_y = [];
        self.rssi_trash_y = [];

        self.avg_snr_ber_ser_x = [];
        self.avg_snr_ber_y = [];
        self.avg_snr_ber_trash_y = [];
        self.avg_snr_ser_y = [];
        self.avg_snr_trash_y = [];

        self.avg_rssi_ber_ser_x = [];
        self.avg_rssi_ber_y = [];
        self.avg_rssi_ber_trash_y = [];
        self.avg_rssi_ser_y = [];
        self.avg_rssi_trash_y = [];

        self.avg_rssi_ber_ser_x_sorted = [];
        self.avg_rssi_ber_y_sorted = [];
        self.avg_rssi_ber_trash_y_sorted = [];
        self.avg_rssi_ser_y_sorted = [];
        self.avg_rssi_trash_y_sorted = [];

        # AGC Attenuations
        self.agc_att_x = [];
        self.agc_att_x_sorted = [];
        self.agc_snr_y = [];
        self.agc_snr_y_sorted = [];
        self.agc_rssi_y = [];
        self.agc_rssi_y_sorted = [];
        self.agc_dropped = [];

        # Gain 4 Attenuations
        self.g4_att_x = [];
        self.g4_att_x_sorted = [];
        self.g4_snr_y = [];
        self.g4_snr_y_sorted = [];
        self.g4_rssi_y = [];
        self.g4_rssi_y_sorted = [];
        self.g4_dropped = [];

        # Gain 6 Attenuations
        self.g6_att_x = [];
        self.g6_att_x_sorted = [];
        self.g6_snr_y = [];
        self.g6_snr_y_sorted = [];
        self.g6_rssi_y = [];
        self.g6_rssi_y_sorted = [];
        self.g6_dropped = [];

        # Totals and Broad Data
        self.total_bits_sent = 0;
        self.total_bit_errors = 0;
        self.total_trash_packets = 0;

        self.total_bits_sent_trash = 0;
        self.total_bit_errors_trash = 0;

        self.max_snr = 0;
        self.min_snr = 0;
        self.max_rssi = 0;
        self.min_rssi = 0;

        self.max_avg_snr = 0;
        self.min_avg_snr = 0;
        self.max_avg_rssi = 0;
        self.min_avg_rssi = 0;

    def add_pkt_snr_data(self, snr, bits_sent, bit_errors, bits_sent_with_trash, bit_errors_with_trash, symbols_sent, symbol_errors, trash):
        if(snr not in self.snr_dict):
            new_dict = {}
            new_dict.update({"Bits Sent": bits_sent});
            new_dict.update({"Bit Errors": bit_errors});
            new_dict.update({"BER": 0}); # We will leave the BER and do a post calculation on it
            new_dict.update({"Bits Sent + Trash": bits_sent_with_trash});
            new_dict.update({"Bit Errors + Trash": bit_errors_with_trash});
            new_dict.update({"BER + Trash": 0});
            new_dict.update({"Symbols Sent": symbols_sent});
            new_dict.update({"Symbol Errors": symbol_errors});
            new_dict.update({"SER": 0}); # We will leave the SER and do a post calculation on it
            new_dict.update({"Trash Packets": 0});
            self.snr_dict.update({snr: new_dict});
        else:
            self.snr_dict.get(snr).update({"Bits Sent": self.snr_dict.get(snr).get("Bits Sent") + bits_sent});
            self.snr_dict.get(snr).update({"Bit Errors": self.snr_dict.get(snr).get("Bit Errors") + bit_errors});
            self.snr_dict.get(snr).update({"Bits Sent + Trash": self.snr_dict.get(snr).get("Bits Sent + Trash") + bits_sent_with_trash});
            self.snr_dict.get(snr).update({"Bit Errors + Trash": self.snr_dict.get(snr).get("Bit Errors + Trash") + bit_errors_with_trash});
            self.snr_dict.get(snr).update({"Symbols Sent": self.snr_dict.get(snr).get("Symbols Sent") + symbols_sent});
            self.snr_dict.get(snr).update({"Symbol Errors": self.snr_dict.get(snr).get("Symbol Errors") + symbol_errors});
            self.snr_dict.get(snr).update({"Trash Packets": self.snr_dict.get(snr).get("Trash Packets") + trash});

    def add_pkt_rssi_data(self, rssi, bits_sent, bit_errors, bits_sent_with_trash, bit_errors_with_trash, symbols_sent, symbol_errors, trash):
        if(rssi not in self.rssi_dict):
            new_dict = {}
            new_dict.update({"Bits Sent": bits_sent});
            new_dict.update({"Bit Errors": bit_errors});
            new_dict.update({"BER": 0}); # We will leave the BER and do a post calculation on it
            new_dict.update({"Bits Sent + Trash": bits_sent_with_trash});
            new_dict.update({"Bit Errors + Trash": bit_errors_with_trash});
            new_dict.update({"BER + Trash": 0});
            new_dict.update({"Symbols Sent": symbols_sent});
            new_dict.update({"Symbol Errors": symbol_errors});
            new_dict.update({"SER": 0}); # We will leave the SER and do a post calculation on it
            new_dict.update({"Trash Packets": 0});
            self.rssi_dict.update({rssi: new_dict});
        else:
            self.rssi_dict.get(rssi).update({"Bits Sent": self.rssi_dict.get(rssi).get("Bits Sent") + bits_sent});
            self.rssi_dict.get(rssi).update({"Bit Errors": self.rssi_dict.get(rssi).get("Bit Errors") + bit_errors});
            self.rssi_dict.get(rssi).update({"Bits Sent + Trash": self.rssi_dict.get(rssi).get("Bits Sent + Trash") + bits_sent_with_trash});
            self.rssi_dict.get(rssi).update({"Bit Errors + Trash": self.rssi_dict.get(rssi).get("Bit Errors + Trash") + bit_errors_with_trash});
            self.rssi_dict.get(rssi).update({"Symbols Sent": self.rssi_dict.get(rssi).get("Symbols Sent") + symbols_sent});
            self.rssi_dict.get(rssi).update({"Symbol Errors": self.rssi_dict.get(rssi).get("Symbol Errors") + symbol_errors});
            self.rssi_dict.get(rssi).update({"Trash Packets": self.rssi_dict.get(rssi).get("Trash Packets") + trash});

    # This function is only for adding in bit/symbol/trash data
    def add_pkt_att_gain_data(self, att_gain, bits_sent, bit_errors, bits_sent_with_trash, bit_errors_with_trash, symbols_sent, symbol_errors, trash, dropped):
        if(att_gain not in self.att_gain_dict):
            new_dict = {};
            new_dict.update({"SNR Mean": 0});
            new_dict.update({"SNR Var": 0});
            new_dict.update({"SNR Std": 0});
            new_dict.update({"RSSI Mean": 0});
            new_dict.update({"RSSI Mean": 0});
            new_dict.update({"RSSI Std": 0});
            new_dict.update({"Bits Sent": bits_sent});
            new_dict.update({"Bit Errors": bit_errors});
            new_dict.update({"BER": 0}); # We will leave the BER and do a post calculation on it
            new_dict.update({"Bits Sent + Trash": bits_sent_with_trash});
            new_dict.update({"Bit Errors + Trash": bit_errors_with_trash});
            new_dict.update({"BER + Trash": 0});
            new_dict.update({"Symbols Sent": symbols_sent});
            new_dict.update({"Symbol Errors": symbol_errors});
            new_dict.update({"SER": 0}); # We will leave the SER and do a post calculation on it
            new_dict.update({"Trash Packets": trash});
            new_dict.update({"Dropped Packets": dropped});
            self.att_gain_dict.update({att_gain: new_dict});
        else:
            self.att_gain_dict.get(att_gain).update({"Bits Sent": self.att_gain_dict.get(att_gain).get("Bits Sent") + bits_sent});
            self.att_gain_dict.get(att_gain).update({"Bit Errors": self.att_gain_dict.get(att_gain).get("Bit Errors") + bit_errors});
            self.att_gain_dict.get(att_gain).update({"Bits Sent + Trash": self.att_gain_dict.get(att_gain).get("Bits Sent + Trash") + bits_sent_with_trash});
            self.att_gain_dict.get(att_gain).update({"Bit Errors + Trash": self.att_gain_dict.get(att_gain).get("Bit Errors + Trash") + bit_errors_with_trash});
            self.att_gain_dict.get(att_gain).update({"Symbols Sent": self.att_gain_dict.get(att_gain).get("Symbols Sent") + symbols_sent});
            self.att_gain_dict.get(att_gain).update({"Symbol Errors": self.att_gain_dict.get(att_gain).get("Symbol Errors") + symbol_errors});
            self.att_gain_dict.get(att_gain).update({"Trash Packets": self.att_gain_dict.get(att_gain).get("Trash Packets") + trash});
            self.att_gain_dict.get(att_gain).update({"Dropped Packets": self.att_gain_dict.get(att_gain).get("Dropped Packets") + dropped});

    def add_pkt_att_gain_snr_rssi(self, att_gain, snr_mean, snr_var, snr_std, 
                                                    rssi_mean, rssi_var, rssi_std):
        if(att_gain not in self.att_gain_dict):
            print("Found issue in code where average SNR and RSSI is added before any data.")
            input(); # Shutdown
        else:
            self.att_gain_dict.get(att_gain).update({"SNR Mean": snr_mean});
            self.att_gain_dict.get(att_gain).update({"SNR Var": snr_var});
            self.att_gain_dict.get(att_gain).update({"SNR Std": snr_std});
            self.att_gain_dict.get(att_gain).update({"RSSI Mean": rssi_mean});
            self.att_gain_dict.get(att_gain).update({"RSSI Var": rssi_var});
            self.att_gain_dict.get(att_gain).update({"RSSI Std": rssi_std});

def which_sf(dir):
    dir_split = dir.split("_");
    if(dir_split[len(dir_split) - 2] == "sp7"):
        return 7;
    elif(dir_split[len(dir_split) - 2] == "sp8"):
        return 8;
    elif(dir_split[len(dir_split) - 2] == "sp9"):
        return 9;
    elif(dir_split[len(dir_split) - 2] == "sp10"):
        return 10;
    elif(dir_split[len(dir_split) - 2] == "sp11"):
        return 11;
    elif(dir_split[len(dir_split) - 2] == "sp12"):
        return 12;

def analyze_directory(dir_path, sf_obj: SF):
    global ignore_list

    files = glob.glob(dir_path+"\\*");

    for file in files:
        if(file in ignore_list):
            print("Over files: Skipping: {}".format(file));
            continue;

        #print("Analyzing: {}".format(file));
        data_file = open(file, "r");

        # Get the attenuation setting from the file name
        attenuation_setting = file.split("\\")[-1].split("_")[-1].split(".")[0];
        agc_gain_setting = file.split("\\")[-2].split("_")[-1];

        file_att_gain = "{}_{}".format(attenuation_setting, agc_gain_setting);
        #print("Att gain: {}".format(file_att_gain));
        snr_points = [];
        rssi_points = [];
        
        data_file = open(file, "r")

        while(True):
            send_pkt_info = data_file.readline().split()
            recv_pkt_info = data_file.readline().split()

            if(len(send_pkt_info) == 0):
                break;

            """
            DROPPED PACKET Condition:
                In the case that there was a packet dropped this would be the condition under which no
                data showed up or came back from the reciever

                Need to add a tracking here based on the setup
            """
            if(len(recv_pkt_info) == 1):
                # Add in a dropped packet to get Dropped v.s. Attenuation
                sf_obj.add_pkt_att_gain_data(file_att_gain, 0, 0, 0, 0, 0, 0, 0, 1);
                continue;

            send_pkt_len = int(send_pkt_info[2]);
            if(send_pkt_len != 255):
                print("Length issue on sender side found in file {} ".format(file));
                print("Packet {}".format(send_pkt_info[0]));
                input(); # Shut down

            """
            TRASH PACKET Condition:
                In the case that there was a packet mangled this be the condition under which
                the packet cannot be unanalyzed and will be referred to as a trash packet
            """
            recv_pkt_len = int(recv_pkt_info[3]);
            recv_snr = float(recv_pkt_info[2]);
            recv_rssi = float(recv_pkt_info[1]);
            if((recv_pkt_len != 255) or 
                (len(recv_pkt_info[4]) != 255)):
                sf_obj.add_pkt_snr_data(recv_snr, 0, 0, send_pkt_len * 8, send_pkt_len * 8, 0, 0, 1);
                sf_obj.add_pkt_rssi_data(recv_rssi, 0, 0, send_pkt_len * 8, send_pkt_len * 8, 0, 0, 1);
                sf_obj.add_pkt_att_gain_data(file_att_gain, 0, 0, send_pkt_len * 8, send_pkt_len * 8, 0, 0, 1, 0);
                sf_obj.total_trash_packets += 1;
                sf_obj.total_bits_sent_trash += (send_pkt_len * 8);
                sf_obj.total_bit_errors_trash += (send_pkt_len * 8);
                continue;

            """
            Data to capture
            """
            bits_sent = send_pkt_len * 8;
            bit_errors = 0;

            symbols_sent = send_pkt_len;
            symbol_errors = 0;
            
            for i in range(0, send_pkt_len):
                if(recv_pkt_info[4][i] != send_pkt_info[1][i]):
                    symbol_errors += 1; # Overall symbol error
                    sent_val = int(send_pkt_info[1][i], 16);
                    recv_val = int(recv_pkt_info[4][i], 16);

                    for j in range(0, 4):
                        if(((recv_val >> j) & 1) != ((sent_val >> j) & 1)):
                            bit_errors += 1;

            sf_obj.add_pkt_snr_data(recv_snr, bits_sent, bit_errors, bits_sent, bit_errors, symbols_sent, symbol_errors, 0);
            sf_obj.add_pkt_rssi_data(recv_rssi, bits_sent, bit_errors, bits_sent, bit_errors, symbols_sent, symbol_errors, 0);
            sf_obj.add_pkt_att_gain_data(file_att_gain, bits_sent, bit_errors, bits_sent, bit_errors, symbols_sent, symbol_errors, 0, 0);

            sf_obj.total_bits_sent += bits_sent;
            sf_obj.total_bit_errors += bit_errors;
            sf_obj.total_bits_sent_trash += bits_sent;
            sf_obj.total_bit_errors_trash += bit_errors;

            snr_points.append(float(recv_snr));
            rssi_points.append(float(recv_rssi));

        snr_mean = "{:.2f}".format(np.average(snr_points));
        snr_var = "{:.2f}".format(np.var(snr_points));
        snr_std = "{:.2f}".format(np.std(snr_points));
        rssi_mean = "{:.2f}".format(np.average(rssi_points));
        rssi_var = "{:.2f}".format(np.var(rssi_points));
        rssi_std = "{:.2f}".format(np.std(rssi_points));

        sf_obj.add_pkt_att_gain_snr_rssi(file_att_gain, snr_mean, snr_var, snr_std,
                                                        rssi_mean, rssi_var, rssi_std);

def print_snr_rssi_dict_entry(key, entry):
    print("\t{}|Bits Sent: {}|Errors: {}|BER: {}|Symbols Sent: {}|Errors: {}|SER: {}|Trash: {}"
            .format(key, entry.get("Bits Sent"), entry.get("Bit Errors"), entry.get("BER"), 
                    entry.get("Symbols Sent"), entry.get("Symbol Errors"), entry.get("SER"),
                    entry.get("Trash Packets")));

def print_att_gain_dict_entry(key, entry):
    print("\t{}|SNR Mean: {}|Var: {}|STD: {}|RSSI Mean: {}|Var: {}|STD:{}"
            .format(key, entry.get("SNR Mean"), entry.get("SNR Var"), entry.get("SNR Std"),
                        entry.get("RSSI Mean"), entry.get("SNR Var"), entry.get("SNR Std")));
    print("\t{}|Bits Sent: {}|Errors: {}|BER: {}|Symbols Sent: {}|Errors: {}|SER: {}|Trash: {}"
            .format(key, entry.get("Bits Sent"), entry.get("Bit Errors"), entry.get("BER"), 
                        entry.get("Symbols Sent"), entry.get("Symbol Errors"), entry.get("SER"),
                        entry.get("Trash Packets")));
    

def main():
    global ignore_list;

    with open("C:\\Users\\KN125\\Documents\\Project_Owl_SPPIF_Work\\Python_Main\\ignore_files.txt") as ignore:
        while(True):
            new_file = ignore.readline().rstrip();
            
            if(len(new_file) == 0):
                break;
            
            ignore_list.append(new_file);

    # Setup across file data structure
    """
    ===============================================================================================
    ===============================================================================================
    """
    sf_dict_over_file = {};
    sf_dict_over_file.update({12: SF(12)});
    sf_dict_over_file.update({11: SF(11)});
    sf_dict_over_file.update({10: SF(10)});
    sf_dict_over_file.update({9: SF(9)});
    sf_dict_over_file.update({8: SF(8)});
    sf_dict_over_file.update({7: SF(7)}); 

    # Start reading through files
    master_path = os.getcwd();

    g6_pkt_dirs = glob.glob(master_path+"\\500_pkt_*_g6");
    for dir in g6_pkt_dirs:
        analyze_directory(dir, sf_dict_over_file.get(which_sf(dir)));

    g4_pkt_dirs = glob.glob(master_path+"\\500_pkt_*_g4");
    for dir in g4_pkt_dirs:
        analyze_directory(dir, sf_dict_over_file.get(which_sf(dir)));
    
    agc_pkt_dirs = glob.glob(master_path+"\\250_pkt_*_agc");
    for dir in agc_pkt_dirs:
        analyze_directory(dir, sf_dict_over_file.get(which_sf(dir)));

    fig_sf_snr_ber, ax_snr_ber = plt.subplots(1, 1);
    fig_sf_snr_ber_and_trash, ax_snr_ber_trash = plt.subplots(1, 1);
    fig_sf_rssi_ber, ax_rssi_ber = plt.subplots(1, 1);
    fig_sf_rssi_ber_and_trash, ax_rssi_ber_trash = plt.subplots(1, 1);
    for sf_obj in sf_dict_over_file.values():
        snr_rssi_table_csv = open("SF{}_SNR_RSSI_Table.csv".format(sf_obj.spreading_factor), "w+");
        snr_rssi_table_csv.write("LNA Gain,Attenuation,SNR Mean,SNR Variance,SNR Std. Dev.,RSSI Mean,RSSI Variance,RSSI Std. Dev.,Bit Errors,Trash Packets,Dropped Packets\n");
        print(sf_obj.spreading_factor);
        print("----------------------------------------------------------------------");
        for snr_key in sf_obj.snr_dict.keys():
            snr_entry = sf_obj.snr_dict.get(snr_key);

            # This is SNR post processing BER calculation
            bits_sent = snr_entry.get("Bits Sent");
            if(bits_sent != 0):
                bit_errors = snr_entry.get("Bit Errors");
                bit_error_rate = bit_errors / bits_sent;
                snr_entry.update({"BER": bit_error_rate});    

            # This is SNR post processing BER + Trash calculation
            bits_sent_trash = snr_entry.get("Bits Sent + Trash");
            if(bits_sent_trash != 0):
                bit_errors_trash = snr_entry.get("Bit Errors + Trash");
                bit_error_rate_trash = bit_errors_trash / bits_sent_trash;
                snr_entry.update({"BER + Trash": bit_error_rate_trash});

            # This is SNR post processing SER calculation
            symbols_sent = snr_entry.get("Symbols Sent");
            symbol_errors = snr_entry.get("Symbol Errors");
            if(symbols_sent != 0):
                symbol_error_rate = symbol_errors / symbols_sent;
                snr_entry.update({"SER": symbol_error_rate});

            sf_obj.snr_ber_ser_x.append(snr_key);
            sf_obj.snr_ber_trash_y.append(snr_entry.get("BER + Trash"));
            sf_obj.snr_ber_y.append(snr_entry.get("BER"));
            sf_obj.snr_ser_y.append(snr_entry.get("SER"));

            #print_snr_rssi_dict_entry(snr_key, snr_entry);

        for rssi_key in sf_obj.rssi_dict.keys():
            rssi_entry = sf_obj.rssi_dict.get(rssi_key);

            # This is RSSI post processing BER calculation
            bits_sent = rssi_entry.get("Bits Sent");
            bit_errors = rssi_entry.get("Bit Errors");
            if(bits_sent != 0):
                bit_error_rate = bit_errors / bits_sent;
                rssi_entry.update({"BER": bit_error_rate});
            
            # This is SNR post processing BER + Trash calculation
            bits_sent_trash = rssi_entry.get("Bits Sent + Trash");
            if(bits_sent_trash != 0):
                bit_errors_trash = rssi_entry.get("Bit Errors + Trash");
                bit_error_rate_trash = bit_errors_trash / bits_sent_trash;
                rssi_entry.update({"BER + Trash": bit_error_rate_trash});

            # This is RSSI post processing SER calculation
            symbols_sent = rssi_entry.get("Symbols Sent");
            symbol_errors = rssi_entry.get("Symbol Errors");
            if(symbols_sent != 0):
                symbol_error_rate = symbol_errors / symbols_sent;
                rssi_entry.update({"SER": symbol_error_rate});

            sf_obj.rssi_ber_ser_x.append(rssi_key);
            sf_obj.rssi_ber_y.append(rssi_entry.get("BER"));
            sf_obj.rssi_ber_trash_y.append(rssi_entry.get("BER + Trash"));
            sf_obj.rssi_ser_y.append(rssi_entry.get("SER"));

            #print_snr_rssi_dict_entry(rssi_key, rssi_entry);
        
        for att_gain_key in sf_obj.att_gain_dict.keys():
            att_gain_entry = sf_obj.att_gain_dict.get(att_gain_key);

            # This is ATT_Gain post processing BER calculation
            bits_sent = att_gain_entry.get("Bits Sent");
            bit_errors = att_gain_entry.get("Bit Errors");
            if(bits_sent != 0):
                bit_error_rate = bit_errors / bits_sent;
                att_gain_entry.update({"BER": bit_error_rate});
                if(bit_error_rate < 0):
                    print_att_gain_dict_entry(att_gain_key, att_gain_entry);

            # This is SNR post processing BER + Trash calculation
            bits_sent_trash = att_gain_entry.get("Bits Sent + Trash");
            if(bits_sent_trash != 0):
                bit_errors_trash = att_gain_entry.get("Bit Errors + Trash");
                bit_error_rate_trash = bit_errors_trash / bits_sent_trash;
                #print("Att_gain: {} | Bits Sent: {} | Bit Errors: {} | BER Trash: {}".format(att_gain_key, bits_sent_trash, bit_errors_trash, bit_error_rate_trash));
                att_gain_entry.update({"BER + Trash": bit_error_rate_trash});

            # This is ATT_Gain post processing SER calculation
            symbols_sent = att_gain_entry.get("Symbols Sent");
            symbol_errors = att_gain_entry.get("Symbol Errors");
            if(symbols_sent != 0):
                symbol_error_rate = symbol_errors / symbols_sent;
                att_gain_entry.update({"SER": symbol_error_rate});
            
            if(not math.isnan(float(att_gain_entry.get("SNR Mean")))):
                sf_obj.avg_snr_ber_ser_x.append(float(att_gain_entry.get("SNR Mean")));
                sf_obj.avg_snr_ber_y.append(att_gain_entry.get("BER"));
                sf_obj.avg_snr_ber_trash_y.append(att_gain_entry.get("BER + Trash"));
                sf_obj.avg_snr_ser_y.append(att_gain_entry.get("SER"));
                sf_obj.avg_snr_trash_y.append(att_gain_entry.get("Trash Packets"));

            if(not math.isnan(float(att_gain_entry.get("RSSI Mean")))):
                sf_obj.avg_rssi_ber_ser_x.append(float(att_gain_entry.get("RSSI Mean")));
                sf_obj.avg_rssi_ber_y.append(att_gain_entry.get("BER"));
                sf_obj.avg_rssi_ber_trash_y.append(att_gain_entry.get("BER + Trash"));
                sf_obj.avg_rssi_ser_y.append(att_gain_entry.get("SER"));
                sf_obj.avg_rssi_trash_y.append(att_gain_entry.get("Trash Packets"));

            if(att_gain_key.split("_")[1] == 'g6'):
                sf_obj.g6_att_x.append(int(att_gain_key.split("_")[0]))
                sf_obj.g6_snr_y.append(float(att_gain_entry.get("SNR Mean")));
                sf_obj.g6_rssi_y.append(float(att_gain_entry.get("RSSI Mean")));
                sf_obj.g6_dropped.append(int(att_gain_entry.get("Dropped Packets")));
                
                """
                print("\tGain 6: Attenuation: {} | SNR Mean: {} | SNR Variance: {} | SNR Std. Dev: {}"
                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("SNR Mean")),
                                float(att_gain_entry.get("SNR Var")), float(att_gain_entry.get("SNR Std"))));
                """
                
                snr_rssi_table_csv.write("6,{},{},{},{},{},{},{},{},{},{}\n"
                                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("SNR Mean")),
                                        float(att_gain_entry.get("SNR Var")), float(att_gain_entry.get("SNR Std")),
                                        float(att_gain_entry.get("RSSI Mean")), float(att_gain_entry.get("RSSI Var")), 
                                        float(att_gain_entry.get("RSSI Std")), int(att_gain_entry.get("Bit Errors")),
                                        int(att_gain_entry.get("Trash Packets")), int(att_gain_entry.get("Dropped Packets"))));
                
                """
                print("\tGain 6: Attenuation: {} | RSSI Mean: {} | RSSI Variance: {} | RSSI Std. Dev: {}"
                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("RSSI Mean")),
                                float(att_gain_entry.get("RSSI Var")), float(att_gain_entry.get("RSSI Std"))));

                print("\n\tGain 6: Attenuation: {} | Total Bits Sent: {} | Total Bits Errors: {} | BER: {}"
                        .format(att_gain_key.split("_")[0], att_gain_entry.get("Bits Sent"), att_gain_entry.get("Bit Errors"), att_gain_entry.get("BER")));
                
                print("\tGatin 6: Attenuation: {} | Bits Sent + Trash: {} | Bit Errors + Trash: {} | BER + Trash: {}\n"
                        .format(att_gain_key.split("_")[0], att_gain_entry.get("Bits Sent + Trash"), att_gain_entry.get("Bit Errors + Trash"), att_gain_entry.get("BER + Trash")));
                """
            elif(att_gain_key.split("_")[1] == 'g4'):
                sf_obj.g4_att_x.append(int(att_gain_key.split("_")[0]))
                sf_obj.g4_snr_y.append(float(att_gain_entry.get("SNR Mean")));
                sf_obj.g4_rssi_y.append(float(att_gain_entry.get("RSSI Mean")));
                sf_obj.g4_dropped.append(int(att_gain_entry.get("Dropped Packets")));
                
                snr_rssi_table_csv.write("4,{},{},{},{},{},{},{},{},{},{}\n"
                                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("SNR Mean")),
                                        float(att_gain_entry.get("SNR Var")), float(att_gain_entry.get("SNR Std")),
                                        float(att_gain_entry.get("RSSI Mean")), float(att_gain_entry.get("RSSI Var")), 
                                        float(att_gain_entry.get("RSSI Std")), int(att_gain_entry.get("Bit Errors")),
                                        int(att_gain_entry.get("Trash Packets")), int(att_gain_entry.get("Dropped Packets"))));
                
                """
                print("\tGain 4: Attenuation: {} | SNR Mean: {} | SNR Variance: {} | SNR Std. Dev: {}"
                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("SNR Mean")),
                                float(att_gain_entry.get("SNR Var")), float(att_gain_entry.get("SNR Std"))));
                print("\tGain 4: Attenuation: {} | RSSI Mean: {} | RSSI Variance: {} | RSSI Std. Dev: {}"
                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("RSSI Mean")),
                                float(att_gain_entry.get("RSSI Var")), float(att_gain_entry.get("RSSI Std"))));
                
                print("\n\tGain 4: Attenuation: {} | Total Bits Sent: {} | Total Bits Errors: {} | BER: {}"
                        .format(att_gain_key.split("_")[0], att_gain_entry.get("Bits Sent"), att_gain_entry.get("Bit Errors"), att_gain_entry.get("BER")));
                
                print("\tGatin 4: Attenuation: {} | Bits Sent + Trash: {} | Bit Errors + Trash: {} | BER + Trash: {}\n"
                        .format(att_gain_key.split("_")[0], att_gain_entry.get("Bits Sent + Trash"), att_gain_entry.get("Bit Errors + Trash"), att_gain_entry.get("BER + Trash")));
                """
            elif(att_gain_key.split("_")[1] == 'agc'):
                sf_obj.agc_att_x.append(int(att_gain_key.split("_")[0]))
                sf_obj.agc_snr_y.append(float(att_gain_entry.get("SNR Mean")));
                sf_obj.agc_rssi_y.append(float(att_gain_entry.get("RSSI Mean")));
                sf_obj.agc_dropped.append(int(att_gain_entry.get("Dropped Packets")));
                
                snr_rssi_table_csv.write("AGC,{},{},{},{},{},{},{},{},{},{}\n"
                                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("SNR Mean")),
                                        float(att_gain_entry.get("SNR Var")), float(att_gain_entry.get("SNR Std")),
                                        float(att_gain_entry.get("RSSI Mean")), float(att_gain_entry.get("RSSI Var")), 
                                        float(att_gain_entry.get("RSSI Std")), int(att_gain_entry.get("Bit Errors")),
                                        int(att_gain_entry.get("Trash Packets")), int(att_gain_entry.get("Dropped Packets"))));
                    
                """
                print("\tGain AGC: Attenuation: {} | SNR Mean: {} | SNR Variance: {} | SNR Std. Dev: {}"
                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("SNR Mean")),
                                float(att_gain_entry.get("SNR Var")), float(att_gain_entry.get("SNR Std"))));
                print("\tGain AGC: Attenuation: {} | RSSI Mean: {} | RSSI Variance: {} | RSSI Std. Dev: {}"
                        .format(att_gain_key.split("_")[0], float(att_gain_entry.get("RSSI Mean")),
                                float(att_gain_entry.get("RSSI Var")), float(att_gain_entry.get("RSSI Std"))));
                
                print("\n\tGain AGC: Attenuation: {} | Total Bits Sent: {} | Total Bits Errors: {} | BER: {}"
                        .format(att_gain_key.split("_")[0], att_gain_entry.get("Bits Sent"), att_gain_entry.get("Bit Errors"), att_gain_entry.get("BER")));
                
                print("\tGatin AGC: Attenuation: {} | Bits Sent + Trash: {} | Bit Errors + Trash: {} | BER + Trash: {}\n"
                        .format(att_gain_key.split("_")[0], att_gain_entry.get("Bits Sent + Trash"), att_gain_entry.get("Bit Errors + Trash"), att_gain_entry.get("BER + Trash")));
                """
            #print_att_gain_dict_entry(att_gain_key, att_gain_entry);
        
        sf_obj.max_snr = max(sf_obj.snr_ber_ser_x);
        sf_obj.max_avg_snr = max(sf_obj.avg_snr_ber_ser_x);
        
        sf_obj.min_snr = min(sf_obj.snr_ber_ser_x);
        sf_obj.min_avg_snr = min(sf_obj.avg_snr_ber_ser_x);

        sf_obj.max_rssi = max(sf_obj.rssi_ber_ser_x);
        sf_obj.max_avg_rssi = max(sf_obj.avg_rssi_ber_ser_x);

        sf_obj.min_rssi = min(sf_obj.rssi_ber_ser_x);
        sf_obj.min_avg_rssi = min(sf_obj.avg_rssi_ber_ser_x);

        print("Spreading Factor: {}".format(sf_obj.spreading_factor));
        print("\tMax SNR: {} | Min SNR: {}".format(sf_obj.max_snr, sf_obj.min_snr));
        print("\tMax Average SNR: {} | Min Average SNR: {}".format(sf_obj.max_avg_snr, sf_obj.min_avg_snr));
        print("\tMax RSSI: {} | Min RSSI: {}".format(sf_obj.max_rssi, sf_obj.min_rssi));
        print("\tMax Average RSSI: {} | Min Average RSSI: {}".format(sf_obj.max_avg_rssi, sf_obj.min_avg_rssi));

        print("\n\tTotal Bits Sent: {} | Total Bit Errors: {}".format(sf_obj.total_bits_sent, sf_obj.total_bit_errors));
        print("\tTotal Bits Sent + Trash: {} | Total Bit Errors + Trash: {} | Total Trash Packets: {}".format(sf_obj.total_bits_sent_trash, sf_obj.total_bit_errors_trash, sf_obj.total_trash_packets));
        """
        fig, ax1 = plt.subplots(1, 1);
        ax1.scatter(sf_obj.snr_ber_ser_x, sf_obj.snr_ber_y);
        ax1.plot(np.unique(sf_obj.snr_ber_ser_x), 
                np.poly1d(np.polyfit(sf_obj.snr_ber_ser_x, sf_obj.snr_ber_y, 5))(np.unique(sf_obj.snr_ber_ser_x)));
        #ax1.legend(loc="upper left");
        ax1.set_title("SF{} BER Chart".format(sf_obj.spreading_factor))
        ax1.set_xlabel("SNR");
        ax1.set_ylabel("BER");
        """
        order = np.argsort(sf_obj.avg_snr_ber_ser_x);
        sf_obj.avg_snr_ber_ser_x_sorted = np.array(sf_obj.avg_snr_ber_ser_x)[order];
        sf_obj.avg_snr_ber_y_sorted = np.array(sf_obj.avg_snr_ber_y)[order];
        sf_obj.avg_snr_ber_trash_y_sorted = np.array(sf_obj.avg_snr_ber_trash_y)[order];

        ax_snr_ber.plot(sf_obj.avg_snr_ber_ser_x_sorted, sf_obj.avg_snr_ber_y_sorted, marker="v", markersize="10", linewidth=3.0, label="{} BER".format(sf_obj.spreading_factor));
        ax_snr_ber_trash.plot(sf_obj.avg_snr_ber_ser_x_sorted, sf_obj.avg_snr_ber_trash_y_sorted, marker="v", markersize="10", linewidth=3.0, label="{} BER".format(sf_obj.spreading_factor));

        order = np.argsort(sf_obj.avg_rssi_ber_ser_x);
        sf_obj.avg_rssi_ber_ser_x_sorted = np.array(sf_obj.avg_rssi_ber_ser_x)[order];
        sf_obj.avg_rssi_ber_y_sorted = np.array(sf_obj.avg_rssi_ber_y)[order];
        sf_obj.avg_rssi_ber_trash_y_sorted = np.array(sf_obj.avg_rssi_ber_trash_y)[order];

        ax_rssi_ber.plot(sf_obj.avg_rssi_ber_ser_x_sorted, sf_obj.avg_rssi_ber_y_sorted, marker="v", markersize="10", linewidth=3.0, label="{} BER".format(sf_obj.spreading_factor));
        ax_rssi_ber_trash.plot(sf_obj.avg_rssi_ber_ser_x_sorted, sf_obj.avg_rssi_ber_trash_y_sorted, marker="v", markersize="10", linewidth=3.0, label="{} BER".format(sf_obj.spreading_factor));
        
        """
        ax_snr_ber.plot(np.unique(sf_obj.avg_snr_ber_ser_x),
                np.poly1d(np.polyfit(sf_obj.avg_snr_ber_ser_x, sf_obj.avg_snr_ber_y, 10))(np.unique(sf_obj.avg_snr_ber_ser_x)), marker="v", markersize="10", linewidth=3.0, label="{} BER".format(sf_obj.spreading_factor));
        ax_snr_ber_trash.plot(np.unique(sf_obj.avg_snr_ber_ser_x),
                np.poly1d(np.polyfit(sf_obj.avg_snr_ber_ser_x, sf_obj.avg_snr_ber_trash_y, 10))(np.unique(sf_obj.avg_snr_ber_ser_x)), marker="^", markersize="10", linewidth=3.0, label="{} BER + Trash".format(sf_obj.spreading_factor));
        ax_rssi_ber.plot(np.unique(sf_obj.avg_rssi_ber_ser_x),
                np.poly1d(np.polyfit(sf_obj.avg_rssi_ber_ser_x, sf_obj.avg_rssi_ber_y, 100))(np.unique(sf_obj.avg_rssi_ber_ser_x)), marker="v", markersize="10", linewidth=3.0, label="{} BER".format(sf_obj.spreading_factor));
        ax_rssi_ber_trash.plot(np.unique(sf_obj.avg_rssi_ber_ser_x),
                np.poly1d(np.polyfit(sf_obj.avg_rssi_ber_ser_x, sf_obj.avg_rssi_ber_trash_y, 100))(np.unique(sf_obj.avg_rssi_ber_ser_x)), marker="^", markersize="10", linewidth=3.0, label="{} BER + Trash".format(sf_obj.spreading_factor));
        """

        order = np.argsort(sf_obj.agc_att_x);
        sf_obj.agc_att_x_sorted = np.array(sf_obj.agc_att_x)[order];
        sf_obj.agc_snr_y_sorted = np.array(sf_obj.agc_snr_y)[order];
        sf_obj.agc_rssi_y_sorted = np.array(sf_obj.agc_rssi_y)[order];

        order = np.argsort(sf_obj.g4_att_x);
        sf_obj.g4_att_x_sorted = np.array(sf_obj.g4_att_x)[order];
        sf_obj.g4_snr_y_sorted = np.array(sf_obj.g4_snr_y)[order];
        sf_obj.g4_rssi_y_sorted = np.array(sf_obj.g4_rssi_y)[order];

        order = np.argsort(sf_obj.g6_att_x);
        sf_obj.g6_att_x_sorted = np.array(sf_obj.g6_att_x)[order];
        sf_obj.g6_snr_y_sorted = np.array(sf_obj.agc_snr_y)[order];
        sf_obj.g6_rssi_y_sorted = np.array(sf_obj.g6_rssi_y)[order];

        fig3, ax3 = plt.subplots(1, 1);
        ax3.plot(sf_obj.agc_att_x_sorted, sf_obj.agc_snr_y_sorted, marker="^", label="AGC", color="royalblue", markersize="10", linewidth=3.0);
        ax3.plot(sf_obj.g6_att_x_sorted, sf_obj.g6_snr_y_sorted, marker="^", label="Gain 6", color="forestgreen", markersize="10", linewidth=3.0);
        ax3.plot(sf_obj.g4_att_x_sorted, sf_obj.g4_snr_y_sorted, marker="^", label="Gain 4", color="orangered", markersize="10", linewidth=3.0);
        ax3.legend(loc="upper right");
        ax3.set_title("SF{} Mean SNR v.s. Attenuation".format(sf_obj.spreading_factor), fontsize=18);
        ax3.set_xlabel("Attenuation", fontsize=20);
        ax3.set_ylabel("Mean SNR", fontsize=20);
        ax3.legend(loc="upper right", fontsize=22);
        ax3.tick_params(axis='x', labelsize=15);
        ax3.tick_params(axis='y', labelsize=15);
        ax3.grid(True);

        fig2, ax2 = plt.subplots(3, 1);
        ax2[0].plot(sf_obj.avg_snr_ber_ser_x_sorted, sf_obj.avg_snr_ber_y_sorted, marker="^", label="BER", color="royalblue", markersize="10", linewidth=3.0);
        ax2[0].legend(loc="upper right");
        ax2[0].set_title("SF{} BER ".format(sf_obj.spreading_factor), fontsize=18);
        ax2[0].set_xlabel("Mean SNR", fontsize=12);
        ax2[0].set_ylabel("Bit Error Rate (BER)", fontsize=12);
        ax2[0].legend(loc="upper right", fontsize=22);
        ax2[0].tick_params(axis='x', labelsize=15);
        ax2[0].tick_params(axis='y', labelsize=15);
        ax2[0].grid(True);

        ax2[1].plot(sf_obj.avg_snr_ber_ser_x_sorted, sf_obj.avg_snr_ber_trash_y_sorted, marker="^", label="BER", color="forestgreen", markersize="10", linewidth=3.0);
        ax2[1].legend(loc="upper right");
        ax2[1].set_title("SF {} BER + Trash v.s. SNR".format(sf_obj.spreading_factor), fontsize=18);
        ax2[1].set_xlabel("Mean SNR", fontsize=12);
        ax2[1].set_ylabel("Bit Error Rate (BER)", fontsize=12);
        ax2[1].legend(loc="upper right", fontsize=18);
        ax2[1].tick_params(axis='x', labelsize=15);
        ax2[1].tick_params(axis='y', labelsize=15);
        ax2[1].grid(True);

        ax2[2].plot(sf_obj.avg_snr_ber_ser_x_sorted, sf_obj.avg_snr_ber_y_sorted, marker="^", markersize="10", label="BER", color="royalblue", linewidth=3.0);
        ax2[2].plot(sf_obj.avg_snr_ber_ser_x_sorted, sf_obj.avg_snr_ber_trash_y_sorted, marker="v", markersize="10", color="forestgreen", linewidth=3.0, label="BER + Trash");
        ax2[2].legend(loc="upper right");
        ax2[2].set_title("SF{} Full BER v.s. SNR".format(sf_obj.spreading_factor), fontsize=18);
        ax2[2].set_xlabel("Mean SNR", fontsize=12);
        ax2[2].set_ylabel("Bit Error Rate (BER)", fontsize=12);
        ax2[2].legend(loc="upper right", fontsize=18);
        ax2[2].tick_params(axis='x', labelsize=15);
        ax2[2].tick_params(axis='y', labelsize=15);
        ax2[2].grid(True);
        print("----------------------------------------------------------------------");


    """
    ===============================================================================================
    ===============================================================================================
    """
    ax_snr_ber.legend(loc="upper right", fontsize=22);
    ax_snr_ber.tick_params(axis='x', labelsize=15);
    ax_snr_ber.tick_params(axis='y', labelsize=15);
    ax_snr_ber.set_title("All SF BER v.s. SNR Chart", fontsize=22);
    ax_snr_ber.set_xlabel("Mean SNR", fontsize=20);
    ax_snr_ber.set_ylabel("Bit Error Rate (BER)", fontsize=20);    
    ax_snr_ber.grid(True);
    ax_snr_ber_trash.legend(loc="upper right", fontsize=22);
    ax_snr_ber_trash.tick_params(axis='x', labelsize=15);
    ax_snr_ber_trash.tick_params(axis='y', labelsize=15);
    ax_snr_ber_trash.set_title("All SF BER v.s. SNR Chart (Including Trash Bits)", fontsize=22);
    ax_snr_ber_trash.set_xlabel("Mean SNR", fontsize=20);
    ax_snr_ber_trash.set_ylabel("Bit Error Rate (BER)", fontsize=20);    
    ax_snr_ber_trash.grid(True);
    ax_rssi_ber.legend(loc="upper right", fontsize=22);
    ax_rssi_ber.tick_params(axis='x', labelsize=15);
    ax_rssi_ber.tick_params(axis='y', labelsize=15);
    ax_rssi_ber.set_title("All SF BER v.s. RSSI Chart", fontsize=22);
    ax_rssi_ber.set_xlabel("Mean RSSI", fontsize=20);
    ax_rssi_ber.set_ylabel("Bit Error Rate (BER)", fontsize=20);    
    ax_rssi_ber.grid(True);
    ax_rssi_ber_trash.legend(loc="upper right", fontsize=22);
    ax_rssi_ber_trash.tick_params(axis='x', labelsize=15);
    ax_rssi_ber_trash.tick_params(axis='y', labelsize=15);
    ax_rssi_ber_trash.set_title("All SF BER v.s. RSSI Chart (Including Trash Bits)", fontsize=22);
    ax_rssi_ber_trash.set_xlabel("Mean RSSI", fontsize=20);
    ax_rssi_ber_trash.set_ylabel("Bit Error Rate (BER)", fontsize=20);    
    ax_rssi_ber_trash.grid(True);
    plt.show()

if __name__ == "__main__":
    main();