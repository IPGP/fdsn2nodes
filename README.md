# fdsn2nodes

fdsn2nodes connects to a FDSN webservice, gets channel inventory and creates a WebObs node architecture. It creates CLB and CNF files for all nodes.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisities

The program was developped using python2.7.

The only dependency is [obspy](http://obspy.org/)

### Installing

Copy the file on your computer and run it as follows :

```sh
python fdsn2nodes.py \[-h\] \[-v\] \[-u BASE_URL\] \[-n NETWORK_CODE\]
              \[-C COUNTRY_CODE\] \[-P NODE_PREFIX\] \[-s STATION_CODES\]
              \[-c CHANNEL_CODES\] \[-o OUTPUT_DIR\] \[-e OUTPUT_ENCODING\]
              \[-V\]
```

Invoke help :

```sh
python fdsn2nodes.py -h
```

Example for PF network, french country code, 'XX' as node name prefix, stations names starting with letter M, HH? channels, output nodes in TEST3 directory, files written in latin-1 encoding : 

```sh
python fdsn2nodes.py -v -u http://hudson:8080 -n PF -C FR -P XX -s M* -c HH? \
                     -o TEST3 -e ISO-8859-1
```

## Contributing

Feel free to contact us for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Patrice Boissier** - *Software engineer - OVPF/IPGP* - [PBoissier](https://github.com/PBoissier) - boissier@ipgp.fr

See also the list of [contributors](https://github.com/IPGP/fdsn2nodes/contributors) who participated in this project.

## License

This project is licensed under the GPLv3 license - see [License](LICENSE.txt) file for details.

