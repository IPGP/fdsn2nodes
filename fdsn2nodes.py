#!/usr/bin/env python
# encoding: utf-8
'''
Sismo.WebObs.fdsn2nodes -- Converts FDSN inventory to WebObs Nodes.

Sismo.WebObs.fdsn2nodes connects to a FDSN webservice, gets channel inventory
and creates a WebObs node architecture. It creates CLB and CNF files for all
nodes.

Examples :
python fdsn2nodes.py -u http://hudson:8080 -n PF -o TEST -c FR -C HHZ -s "M*"

python fdsn2nodes.py -v -u http://hudson:8080 -n PF -C FR -P XX -s M* -c HH? \
-o TEST3 -e ISO-8859-1

@author:     Patrice Boissier

@copyright:  2016 OVPF/IPGP. All rights reserved.

@license:    This project is licensed under the GNU General Pyblic License v3.0

@contact:    boissier@ipgp.fr
@deffield    updated: Updated

:copyright:
    Patrice Boissier (boissier@ipgp.fr), 2016
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import sys
import os
import re
import datetime
import codecs
import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from obspy.clients.fdsn import Client

__all__ = []
__version__ = 1.0
__date__ = '2016-02-22'
__updated__ = '2018-11-22'


class NodesCreator(object):
    '''
    WebObs Nodes creator
    '''
    def __init__(self, output_dir, output_encoding):
        '''
        Constructor

        :type output_dir: str
        :param output_dir: A string reprensenting NODES
            output directory.
        :type output_encoding: str
        :param output_encoding: A string reprensenting output
            files encoding.
        '''
        self.output_dir = output_dir
        self.output_encoding = output_encoding
        # Creates output directory if it does not exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_clb_file(self, node_path, node_name, network_code, station):
        '''
        Creates WebObs Node calibration file from class
        :class:`~obspy.core.inventory.station.Station`

        :type node_path: str
        :param node_path: A string representing the path to write Nodes to
        :type node_name: str
        :param node_name: A string representing the Node name (WebObs
            naming convention)
        :type network_code: str
        :param network_code: A string representing the FDSN network code
        :type station: :class:`~obspy.core.inventory.station.Station`
        :param station: the station to create the CLB file from.
        '''
        file_name = "%s/%s.clb" % (node_path, node_name)
        # Used to increment channel index in calibration file
        previous_channel_code = "NA"
        index = 0
        # A WebObs Node needs to have a sample rate and a sensor type
        # at station level, so we use the last current ones we found
        last_sample_rate = "NA"
        last_sensor = "NA"
        lines = list()
        for channel in station.channels:
            if channel.code != previous_channel_code:
                index += 1
            logging.info("|  |--Processing %s channel (%s)" % (channel.code,
                                                               index))
            previous_channel_code = channel.code
            if channel.end_date is None and channel.sample_rate:
                last_sample_rate = channel.sample_rate
            if channel.end_date is None and channel.sensor.type:
                last_sensor = channel.sensor.type
            start_date = channel.start_date.strftime("%Y-%m-%d")
            start_time = channel.start_date.strftime("%H:%M")
            unit = channel.response.instrument_sensitivity.input_units
            gain = 1 / float(channel.response.instrument_sensitivity.value)
            channel_line = "%s|%s|%s|%s|%s||%s|0|%s|%s|||%s|%s|%s|%s|%s|%s" \
                           "||%s\n" % (start_date,
                                       start_time,
                                       str(index),
                                       channel.code,
                                       unit,
                                       channel.code,
                                       str(gain),
                                       str(1),
                                       channel.azimuth,
                                       channel.latitude,
                                       channel.longitude,
                                       channel.elevation,
                                       channel.depth,
                                       channel.sample_rate,
                                       channel.location_code)
            lines.append(channel_line)
        lines.sort()
        # TODO : check if encoding is valid
        clb_file = codecs.open(file_name, 'w', self.output_encoding)
        for line in lines:
            clb_file.write(line)
        clb_file.close()
        # CNF file is created right after because it needs the
        # sensor and sample rate
        self.create_cnf_file(node_path=node_path,
                             node_name=node_name,
                             network_code=network_code,
                             station=station,
                             sample_rate=last_sample_rate,
                             sensor_description=last_sensor)

    def create_cnf_file(self, node_path, node_name, network_code, station,
                        sample_rate, sensor_description="NA"):
        '''
        Creates WebObs Node configuration file from class
        :class:`~obspy.core.inventory.station.Station`

        :type node_path: str
        :param node_path: A string representing the path to write Nodes to
        :type node_name: str
        :param node_name: A string representing the Node name (WebObs
            naming convention)
        :type network_code: str
        :param network_code: A string representing the FDSN network code
        :type station: :class:`~obspy.core.inventory.station.Station`
        :param station: the station to create the CLB file from.
        :type sample_rate: float
        :param sample_rate: A float representing the sensor sample rate
        :type sensor_description: str, optional
        :param sensor_description: A string representing the sensor description
        '''

        file_name = "%s/%s.cnf" % (node_path, node_name)
        contents = station.get_contents()
        # TODO : check if encoding is valid
        cnf_file = codecs.open(file_name, 'w', self.output_encoding)
        cnf_file.write("=key|value\n")
        cnf_file.write('NAME|"%s"\n' % (contents["stations"][0]))
        cnf_file.write("ALIAS|%s\n" % (station.code))
        cnf_file.write("TYPE|%s\n" % (sensor_description))
        cnf_file.write("FID|%s\n" % (station.code))
        cnf_file.write("FDSN_NETWORK_CODE|%s\n" % (network_code))
        cnf_file.write("VALID|1\n")
        cnf_file.write("LAT_WGS84|%s\n" % (str(station.latitude)))
        cnf_file.write("LON_WGS84|%s\n" % (str(station.longitude)))
        cnf_file.write("ALTITUDE|%s\n" % (str(station.elevation)))
        cnf_file.write("POS_DATE|%s\n" % (datetime.date.today().isoformat()))
        cnf_file.write("POS_TYPE|\n")
        cnf_file.write("INSTALL_DATE|%s\n" % (station.creation_date.
                                              strftime("%Y-%m-%d")))
        if station.termination_date is None:
            cnf_file.write("END_DATE|NA\n")
        else:
            cnf_file.write("END_DATE|%s\n" % (station.termination_date.
                                              strftime("%Y-%m-%d")))
        cnf_file.write("ACQ_RATE|1/%s\n" % (str(86400*sample_rate)))
        cnf_file.write("UTC_DATA|+0\n")
        cnf_file.write("LAST_DELAY|1/24\n")
        cnf_file.write("FILES_FEATURES|sensor\n")
        cnf_file.write("TRANSMISSION|\n")
        cnf_file.write("PROC|\n")
        cnf_file.write("VIEW|\n")
        cnf_file.close()

    def create_nodes_from_fdsn(self, base_url, network_code, station_codes,
                               channel_codes, location_codes, country_code="",
                               node_prefix=""):
        '''
        Creates WebObs Nodes architecture and configuration files from FDSN
        Web Service (fdsnws)

        :type base_url: str
        :param base_url: A string representing the FDSN provider URL.
        :type network_code: str
        :param network_code: A string representing the FDSN network code.
        :type station_codes: str
        :param station_codes: A string representing the FDSN station(s)
            (wildcard accepted).
        :type channel_codes: str
        :param channel_codes: A string representing the FDSN channel(s)
            (wildcard accepted).
        :type location_codes: str
        :param location_codes: A string representing the FDSN location
            code(s) (wildcard accepted).
        :type country_code: str, optional
        :param country_code: A string representing the country code.
        :type node_prefix: str, optional
        :param node_prefix: A string representing the node prefix.
        '''
        # Connect to FDSN web service and retrieve inventory
        fdsn_client = Client(base_url=base_url)
        inventory = fdsn_client.get_stations(network=network_code,
                                             station=station_codes,
                                             channel=channel_codes,
                                             location=location_codes,
                                             level="response")
        for network in inventory.networks:
            logging.info("Processing %s network" % (network.code))
            for station in network.stations:
                logging.info("|--Processing %s station" % (station.code))
                # Create node name and path
                node_name = "%s%s%s" % (country_code, node_prefix,
                                        station.code)
                node_path = "%s/%s" % (self.output_dir, node_name)
                # Create file tree and files
                if not os.path.exists(node_path):
                    os.makedirs(node_path)
                    os.makedirs("%s/DOCUMENTS/THUMBNAILS" % (node_path))
                    os.makedirs("%s/FEATURES" % (node_path))
                    os.makedirs("%s/INTERVENTIONS" % (node_path))
                    os.makedirs("%s/PHOTOS/THUMBNAILS" % (node_path))
                    os.makedirs("%s/SCHEMAS/THUMBNAILS" % (node_path))
                    open("%s/acces.txt" % (node_path), 'a').close()
                    open("%s/info.txt" % (node_path), 'a').close()
                    open("%s/installation.txt" % (node_path), 'a').close()
                    open("%s/%s.kml" % (node_path, node_name), 'a').close()
                    open("%s/FEATURES/sensor.txt" % (node_path), 'a').close()
                    open("%s/INTERVENTIONS/%s_Projet.txt" %
                         (node_path, node_name), 'a').close()
                    self.create_clb_file(node_path=node_path,
                                         node_name=node_name,
                                         network_code=network.code,
                                         station=station)


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

  Licensed under the GNU General Pyblic License v3.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose", action="count",
                            help="set verbosity level [default: %(default)s]",
                            required=False)
        parser.add_argument("-u", "--base-url", dest="base_url",
                            help="Defines FDSN base URL. Mandatory.",
                            required=True, type=str)
        parser.add_argument("-n", "--network", dest="network_code",
                            help="Defines the network code. Mandatory.",
                            required=True, type=str)
        parser.add_argument("-C", "--country", dest="country_code",
                            help="Defines the country code. Optional.",
                            required=False, type=str, default="")
        parser.add_argument("-P", "--node_prefix", dest="node_prefix",
                            help="Defines the NODE name prefix code.",
                            required=False, type=str, default="")
        parser.add_argument("-s", "--station-codes", dest="station_codes",
                            help="Defines one or more SEED station codes. "
                            "Accepts wildcards and lists..",
                            required=False, type=str, default="*")
        parser.add_argument("-c", "--channel-codes", dest="channel_codes",
                            help="Defines one or more SEED channel codes. "
                            "Accepts wildcards and lists..",
                            required=False, type=str, default="*")
        parser.add_argument("-l", "--location-codes", dest="location_codes",
                            help="Defines one or more SEED location codes. "
                            "Accepts wildcards and lists..",
                            required=False, type=str, default="*")
        parser.add_argument("-o", "--output-dir", dest="output_dir",
                            help="Defines nodes directory output. "
                            "Default value : ./NODES",
                            required=False, type=str, default="./NODES")
        parser.add_argument("-e", "--output-encoding", dest="output_encoding",
                            help="Defines output files encoding. "
                            "Default value : UTF-8",
                            required=False, type=str, default="utf_8")
        parser.add_argument('-V', '--version', action='version',
                            version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        logging.debug(args)
        # Verbose arg
        verbose = args.verbose
        if verbose is None:
            verbose = 0

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

        # Station codes arg
        station_codes = args.station_codes
        if station_codes:
            station_codes_re = re.compile('^([A-Z0-9]|\*|\?)+'
                                          '(,([A-Z0-9]|\*|\?)*)*$')
            if not station_codes_re.match(station_codes):
                raise Exception('Invalid station code. Station code consist '
                                'of at least one alphanumeric character. '
                                'Wildcards (* and ?) accepted')

        # Channel codes arg
        channel_codes = args.channel_codes
        if channel_codes:
            channel_codes_re = re.compile('^([A-Z0-9]|\*|\?)+$')
            if not channel_codes_re.match(channel_codes):
                raise Exception('Invalid channel code. Channel code consist '
                                'of at least one alphanumeric character. '
                                'Wildcards (* and ?) accepted')

        # Location codes arg
        location_codes = args.location_codes
        if location_codes:
            location_codes_re = re.compile('^([A-Z0-9]|\*|\?)+$')
            if not location_codes_re.match(location_codes):
                raise Exception('Invalid location code. Location code consist '
                                'of two alphanumeric character. '
                                'Wildcards (* and ?) accepted')

        # Output directory arg
        output_dir = args.output_dir

        # Output encoding arg
        output_encoding = args.output_encoding

        logging_level = logging.CRITICAL
        if verbose == 1:
            logging_level = logging.INFO
            print("INFO mode on")
        elif verbose > 1:
            logging_level = logging.DEBUG
            print("DEBUG mode on")
        logging.basicConfig(stream=sys.stdout, level=logging_level)

        print("Instanciation de NodeCreator")
        node_creator = NodesCreator(output_dir=output_dir,
                                    output_encoding=output_encoding)
        print("Creation des NODES")
        node_creator.create_nodes_from_fdsn(base_url=base_url,
                                            network_code=network_code,
                                            station_codes=station_codes,
                                            channel_codes=channel_codes,
                                            location_codes=location_codes,
                                            country_code=country_code,
                                            node_prefix=node_prefix)
        return 0
    except KeyboardInterrupt:
        print("Exiting...")
        return 0
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
