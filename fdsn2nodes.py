#!/usr/local/bin/python2.7
# encoding: utf-8
'''
Sismo.WebObs.fdsn2nodes -- Converts FDSN inventory to WebObs Nodes.

Sismo.WebObs.fdsn2nodes connects to a FDSN webservice, gets channel inventory
and creates a WebObs node architecture. It creates CLB and CNF files for all
nodes.

TODO :
* Handle exception (file and dirs ownership, server availability, etc.)
* Check argument values
* Verbose mode
* Specify WebObs PROC and VIEW for the NODES

Examples :
python fdsn2nodes.py -u http://hudson:8080 -n PF -o TEST -c FR -C HHZ -s "M*"

python fdsn2nodes.py -v -u http://hudson:8080 -n PF -C FR -P XX -s M* -c HH? \
-o TEST3 -e ISO-8859-1

@author:     Patrice Boissier

@copyright:  2016 OVPF/IPGP. All rights reserved.

@license:    TODO

@contact:    boissier@ipgp.fr
@deffield    updated: Updated
'''

from __future__ import division
import sys
import os
import re
import datetime
import codecs
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from obspy.clients.fdsn import Client
from obspy.core import UTCDateTime

__all__ = []
__version__ = 0.1
__date__ = '2016-02-22'
__updated__ = '2016-02-22'


class NodesCreator(object):
    '''
    WebObs Nodes creator
    '''
    def __init__(self, output_dir, output_encoding):
        '''
        Constructor

        :type output_dir: String.
        :param output_dir: the NODES output directory.
        '''
        self.output_dir = output_dir
        self.output_encoding = output_encoding
        # Creates output directory if it does not exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_clb_file(self, file_name, station):
        '''
        Creates WebObs Node calibration file

        :type file_name: String.
        :param file_name: the calibration file name.
        :type station: Station.
        :param station: the station.
        '''
        clb_file = codecs.open(file_name, 'w', self.output_encoding)
        for channel in station.get_channels():
            (channel_start_date, channel_start_time) = channel.get_start_time()
            channel_line = "%s|%s|%s|%s|%s||%s|0|%s|%s|||%s|%s|%s|%s|%s|%s" \
                           "||%s\n" % (channel_start_date, channel_start_time,
                                       channel.get_index(),
                                       channel.get_channel_name(),
                                       "um/s", channel.get_channel_name(),
                                       str(channel.get_gain()), str(10 ** 6),
                                       channel.get_azimuth(),
                                       str(channel.get_latitude()),
                                       str(channel.get_longitude()),
                                       str(channel.get_elevation()),
                                       str(channel.get_depth()),
                                       str(channel.get_sample_rate()),
                                       str(channel.get_location())
                                       )
            clb_file.write(channel_line)
        clb_file.close()

    def create_cnf_file(self, file_name, station):
        '''
        Creates WebObs Node configuration file

        :type file_name: String.
        :param file_name: the configuration file name.
        :type station: Station.
        :param station: the station.
        '''
        cnf_file = codecs.open(file_name, 'w', self.output_encoding)
        cnf_file.write("=key|value\n")
        cnf_file.write('NAME|"%s"\n' % (station.get_site_name()))
        cnf_file.write("ALIAS|%s\n" % (station.get_name()))
        cnf_file.write("TYPE|%s\n" % (station.get_sensor_description()))
        cnf_file.write("FID|%s\n" % (station.get_name()))
        cnf_file.write("FDSN_NETWORK_CODE|%s\n" % (station.get_network()))
        cnf_file.write("VALID|1\n")
        cnf_file.write("LAT_WGS84|%s\n" % (str(station.get_latitude())))
        cnf_file.write("LON_WGS84|%s\n" % (str(station.get_longitude())))
        cnf_file.write("ALTITUDE|%s\n" % (str(station.get_elevation())))
        cnf_file.write("POS_DATE|%s\n" % (datetime.date.today().isoformat()))
        cnf_file.write("POS_TYPE|\n")
        cnf_file.write("INSTALL_DATE|%s\n" % (station.get_start_date()))
        cnf_file.write("END_DATE|%s\n" % (station.get_end_date()))
        cnf_file.write("ACQ_RATE|%s\n" % (str(station.get_sample_rate())))
        cnf_file.write("UTC_DATA|+0\n")
        cnf_file.write("LAST_DELAY|1/24\n")
        cnf_file.write("FILES_FEATURES|sensor\n")
        cnf_file.write("TRANSMISSION|\n")
        cnf_file.write("PROC|\n")
        cnf_file.write("VIEW|\n")
        cnf_file.close()

    def create_nodes_from_fdsn(self, base_url, network_code, station_codes,
                               channel_codes, country_code="", node_prefix=""):
        '''
        Creates WebObs Nodes architecture and configuration files

        :type base_url: String.
        :param base_url: the FDSN provider URL.
        :type network_code: String.
        :param network_code: the FDSN network code.
        :type station_codes: String.
        :param station_codes: the FDSN station(s) (wildcard accepted).
        :type channel_codes: String.
        :param channel_codes: the FDSN channel(s) (wildcard accepted).
        :type country_code: String.
        :param country_code: the country code (optionnal).
        :type node_prefix: String.
        :param node_prefix: the node prefix (optionnal).
        '''
        # Connect to FDSN web service
        fdsn_client = Client(base_url=base_url)
        starttime = UTCDateTime("2001-01-01")
        endtime = UTCDateTime("2016-07-22")
        inventory = fdsn_client.get_stations(network=network_code,
                                             station=station_codes,
                                             starttime=starttime,
                                             endtime=endtime)
        print(inventory)
        # inventory.plot(projection="local")

#         fdsn = FdsnWebService(hostname, tcp_port, base_url, network_code)
#         # Parses stations
#         stations = fdsn.parse_stations(station_name)
#         for station in stations:
#             print("Processing station %s..." % (station.get_name()))
#             # Parses channels
#             fdsn.parse_channels(channels, station)
#             node_name = "%s%s%s%s" % (country_code, node_prefix,
#                                       station.get_digitizer_type(),
#                                       station.get_name())
#             node_path = "%s/%s" % (self.output_dir, node_name)
#             # Creates Node directory and files
#             if not os.path.exists(node_path):
#                 os.makedirs(node_path)
#                 os.makedirs("%s/DOCUMENTS/THUMBNAILS" % (node_path))
#                 os.makedirs("%s/FEATURES" % (node_path))
#                 os.makedirs("%s/INTERVENTIONS" % (node_path))
#                 os.makedirs("%s/PHOTOS/THUMBNAILS" % (node_path))
#                 os.makedirs("%s/SCHEMAS/THUMBNAILS" % (node_path))
#                 open("%s/acces.txt" % (node_path), 'a').close()
#                 open("%s/info.txt" % (node_path), 'a').close()
#                 open("%s/installation.txt" % (node_path), 'a').close()
#                 open("%s/%s.kml" % (node_path, node_name), 'a').close()
#                 open("%s/FEATURES/sensor.txt" % (node_path), 'a').close()
#                 open("%s/INTERVENTIONS/%s_Projet.txt" %
#                      (node_path, node_name), 'a').close()
#                 self.create_cnf_file("%s/%s.cnf" % (node_path, node_name),
#                                      station)
#                 self.create_clb_file("%s/%s.clb" % (node_path, node_name),
#                                      station)


def main(argv=None):
    '''
    Command line options.
    '''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version,
                                                     program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Patrice Boissier on %s.
  Copyright 2016 OVPF/IPGP. All rights reserved.

  Licensed under

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count",
                            help="set verbosity level [default: %(default)s]")
        parser.add_argument("-u", "--base-url", dest="base_url",
                            help="Defines FDSN base URL. Mandatory.")
        parser.add_argument("-n", "--network", dest="network_code",
                            help="Defines the network code. Mandatory.")
        parser.add_argument("-C", "--country", dest="country_code",
                            help="Defines the country code. Optional.")
        parser.add_argument("-P", "--node_prefix", dest="node_prefix",
                            help="Defines the NODE name prefix code.")
        parser.add_argument("-s", "--station-codes", dest="station_codes",
                            help="Defines one or more SEED station codes. "
                            "Accepts wildcards and lists..")
        parser.add_argument("-c", "--channel-codes", dest="channel_codes",
                            help="Defines one or more SEED channel codes. "
                            "Accepts wildcards and lists..")
        parser.add_argument("-o", "--output-dir", dest="output_dir",
                            help="Defines nodes directory output. "
                            "Default value : ./NODES")
        parser.add_argument("-e", "--output-encoding", dest="output_encoding",
                            help="Defines output files encoding. "
                            "Default value : UTF-8")
        parser.add_argument('-V', '--version', action='version',
                            version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        # Verbose arg
        verbose = args.verbose

        # Base URL arg
        base_url = args.base_url

        # Network code arg
        network_code = args.network_code
        if network_code:
            network_code_re = re.compile('^[A-Z0-9]{2}$')
            if not network_code_re.match(network_code):
                raise Exception('Invalid network code. FDNS network codes '
                                'consist of a two alphanumeric character '
                                'code.')

        # Country code arg
        country_code = args.country_code
        if country_code:
            country_code_re = re.compile('^[A-Z0-9]{2}$')
            if not country_code_re.match(country_code):
                raise Exception('Invalid country code. Country codes consist '
                                'of a two alphanumeric character code.')

        # Node prefix arg
        node_prefix = args.node_prefix
        if node_prefix:
            node_prefix_re = re.compile('^[A-Z0-9]+$')
            if not node_prefix_re.match(node_prefix):
                raise Exception('Invalid node prefix. Node prefix consist '
                                'of at least one alphanumeric character.')
        else:
            node_prefix = ""

        # Station codes arg
        station_codes = args.station_codes
        if station_codes:
            station_codes_re = re.compile('^([A-Z0-9]|\*|\?)+$')
            if not station_codes_re.match(station_codes):
                raise Exception('Invalid station code. Station code consist '
                                'of at least one alphanumeric character. '
                                'Wildcards (* and ?) accepted')
        else:
            station_codes = "*"

        # Channel codes arg
        channel_codes = args.channel_codes
        if channel_codes:
            channel_codes_re = re.compile('^([A-Z0-9]|\*|\?)+$')
            if not channel_codes_re.match(channel_codes):
                raise Exception('Invalid channel code. Channel code consist '
                                'of at least one alphanumeric character. '
                                'Wildcards (* and ?) accepted')
        else:
            channel_codes = "*"

        # Output directory arg
        output_dir = args.output_dir
        if not output_dir:
            output_dir = "./NODES"

        # Output encoding arg
        output_encoding = args.output_encoding
        if not output_encoding:
            output_encoding = 'utf_8'

        if verbose > 0:
            print("Verbose mode on")

        if base_url and network_code:
            node_creator = NodesCreator(output_dir, output_encoding)
            node_creator.create_nodes_from_fdsn(base_url, network_code,
                                                station_codes, channel_codes,
                                                country_code, node_prefix)
        else:
            sys.stderr.write("Mandatory argument missing,"
                             " for help use --help\n")

        return 0
    except KeyboardInterrupt:
        print("Exiting...")
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2

if __name__ == "__main__":
    sys.exit(main())
