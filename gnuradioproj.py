#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Gnuradioflow
# Generated: Fri Jun 24 09:28:01 2016
##################################################

from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import time
import numpy as np
from scipy import signal
import os


class gnuradioflow(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Gnuradioflow")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 25e6
        self.constellation = constellation = digital.constellation_calcdist(([-1, 1]), ([0, 1]), 4, 1).base()
        self.center_freq = center_freq = 915.1e6

        ##################################################
        # Blocks
        ##################################################
        self.usrp_source = uhd.usrp_source(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.usrp_source.set_samp_rate(samp_rate)
        #self.usrp_source.set_time_unknown_pps(uhd.time_spec())
        self.usrp_source.set_center_freq(center_freq, 0)
        self.usrp_source.set_gain(20, 0)
        self.usrp_source.set_antenna("RX2", 0)
        self.usrp_source.set_bandwidth(samp_rate, 0)
        self.usrp_sink = uhd.usrp_sink(
        	",".join(("", "")),
        	uhd.stream_args(
        		cpu_format="fc32",
        		channels=range(1),
        	),
        )
        self.usrp_sink.set_samp_rate(samp_rate)
        #self.usrp_sink.set_time_unknown_pps(uhd.time_spec())
        self.usrp_sink.set_center_freq(center_freq, 0)
        self.usrp_sink.set_gain(3, 0)
        self.usrp_sink.set_antenna("TX/RX", 0)
        self.usrp_sink.set_bandwidth(samp_rate, 0)

	#set USRP start time...
	start_time=self.usrp_sink.get_time_now().get_real_secs()+.1
	self.usrp_sink.set_start_time(uhd.time_spec(start_time))
	self.usrp_source.set_start_time(uhd.time_spec(start_time))
	#print "time is now: %d",int(start_time)-5
	#print "test starting at: %d",int(start_time)

        self.digital_glfsr_source_x_0 = digital.glfsr_source_b(7, False, 0, 1)
        self.digital_constellation_modulator_0 = digital.generic_mod(
          constellation=constellation,
          differential=True,
          samples_per_symbol=2,
          pre_diff_code=True,
          excess_bw=0.35,
          verbose=False,
          log=False,
          )
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_vcc((0.5, ))
        self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, 3000000)
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_gr_complex*1, "/home/mewing/Desktop/rxwave", False)
        self.blocks_file_sink_1.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, "/home/mewing/Desktop/txwave", False)
        self.blocks_file_sink_0.set_unbuffered(False)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_head_0, 0), (self.blocks_file_sink_1, 0))    
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.usrp_sink, 0))    
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_file_sink_0, 0))    
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_multiply_const_vxx_0, 0))    
        self.connect((self.digital_glfsr_source_x_0, 0), (self.digital_constellation_modulator_0, 0))    
        self.connect((self.usrp_source, 0), (self.blocks_head_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_head_0.set_length(int(self.samp_rate/8))
        self.usrp_sink.set_samp_rate(self.samp_rate)
        self.usrp_sink.set_bandwidth(self.samp_rate, 0)
        self.usrp_source.set_samp_rate(self.samp_rate)
        self.usrp_source.set_bandwidth(self.samp_rate, 0)

    def get_constellation(self):
        return self.constellation

    def set_constellation(self, constellation):
        self.constellation = constellation

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.usrp_sink.set_center_freq(self.center_freq, 0)
        self.usrp_source.set_center_freq(self.center_freq, 0)

def main(top_block_cls=gnuradioflow, options=None):

    tb = top_block_cls()
    tb.start()
    tb.wait()
	
    samples = []
    errors = 0
    i = 1
    #Set rMax to (num samples) - 1
    rMax = 101

    #Run simulation
    while i < rMax:
    	tb = top_block_cls()
    	tb.start()
    	tb.wait()

    	rx_read_complex_binary = np.fromfile('rxwave', dtype=np.complex64)
    	tx_read_complex_binary = np.fromfile('txwave', dtype=np.complex64)
    	rx = rx_read_complex_binary.real
    	tx = tx_read_complex_binary.real
	
	    z = signal.fftconvolve(tx, rx[::-1])
    	samp = np.argmax(abs(z))
	
        #Check sample for error
        if (samp < 2999943 or samp > 2999945):
            errors += 1
        else:
            #Print successful trial number
            print "Trial " + str(i) + ": " + str(samp)
            samples.append(samp)
            i += 1

    #Print correct samples, successful trials, and number of errors
    print "Final results: " + str(samples)
    print "Correct trials: " + str(i - 1)
    print "Errors: " + str(errors)

    #Write correct samples to file
    sl = open('/home/mewing/Desktop/Samples.m', 'w')
    sl.write(str(samples))
    sl.close()
    

if __name__ == '__main__':
    main()
