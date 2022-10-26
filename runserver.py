import sys
import app
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int,
    help = "the port at which the server should listen")
    args = parser.parse_args()
    port = args.port

    try:
        app.app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()