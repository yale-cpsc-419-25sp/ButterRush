""" Script to start running our Flask app. """

import argparse
from sys import stderr
from app import app

def main():
    """ Starts the server. """

    parser = argparse.ArgumentParser(allow_abbrev=False, description="BUTTERRUSH")
    parser.add_argument(metavar="port", help="the port at which the server should listen", dest="port")
    args = parser.parse_args()

    if not args.port or not args.port.isdigit() or int(args.port) > 65536 or int(args.port) < 0:
        print("Port argument must be numeric and be between 0-65536", file=stderr)
        exit(1)

    port = int(args.port)

    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

    return 0

if __name__ == "__main__":
    main()
