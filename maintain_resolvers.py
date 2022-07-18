#!/usr/bin/python3

from argparse import ArgumentParser
import os.path
import logging
import logging.config
import subprocess

# The program will default to these values unless executed with arguments from the terminal
# Default values
MINIMUM_RESOLVERS = 100
WORK_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
RESOLVERS_FILE = os.path.join(WORK_DIRECTORY, "resolvers.txt")
TEMP_FILE = os.path.join(WORK_DIRECTORY, "resolvers.tmp")
LOG_FILE = os.path.join(WORK_DIRECTORY, "app.log")
DEFAULT_OUTPUT_METHOD = "CONSOLE"  # Options: 'CONSOLE' or 'LOG'
THREADS = 5

parser = ArgumentParser(description="Manage a list of reliable domain resolvers using DNSValidator")
parser.add_argument("-m", "--minimum", default=MINIMUM_RESOLVERS, type=int, help="Minimum number of resolvers in file")
parser.add_argument("-r", "--resolvers", default=RESOLVERS_FILE, help="File containing resolvers to check")
parser.add_argument("-t", "--threads", default=THREADS, type=int, help="Number of threads to use for dnsvalidator")
parser.add_argument("-l", "--logfile", default=LOG_FILE, help="Path to logfile")
parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_METHOD, help="How to handle this programs output - "
                                                                          "options = 'log' or 'console'",)


# Choose where to output to by returning a dictionary with the logging options
def get_output_type(output_arg, log_file):

    try:
        if output_arg.upper() == "CONSOLE":

            log_config = {
                "version": 1,
                "root": {
                    "handlers": ["console"],
                    "level": "INFO"
                },
                "handlers": {
                    "console": {
                        "formatter": "default",
                        "class": "logging.StreamHandler",
                        "level": "INFO"
                    }
                },
                "formatters": {
                    "default": {
                        "format": "[%(asctime)s] %(message)s",
                        "datefmt": "%d-%m-%Y %H:%M:%S",
                    }
                }
            }

        elif output_arg.upper() == "LOG":

            log_config = {
                "version": 1,
                "root": {
                    "handlers": ["file"],
                    "level": "INFO"
                },
                "handlers": {
                    "file": {
                        "formatter": "default",
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "INFO",
                        "filename": log_file,
                        "maxBytes": 1024*1024,
                        "backupCount": 1,
                        "encoding": "utf-8"
                    }
                },
                "formatters": {
                    "default": {
                        "format": "[%(asctime)s] %(message)s",
                        "datefmt": "%d-%m-%Y %H:%M:%S"
                    }
                }
            }

        else:
            logging.error(f"Error: Check your output option: {output_arg.upper()}")
            exit()

    except Exception as e:
        logging.error(f"Error: Should not get here: {e}")
        exit()

    return log_config


# Check dnsvalidator is in the current users $PATH - return executable location
def check_dnsvalidator():

    try:
        check = subprocess.check_output(["which", "dnsvalidator"], shell=False)

    except subprocess.CalledProcessError as e:
        logging.error(f"Error: Could not find executable location: {e}")
        exit()

    return check.decode("utf-8").splitlines()


# Read resolvers into a list and return the length
def check_current_file(resolvers):

    try:
        with open(resolvers, 'r') as resolvers_file:
            current = resolvers_file.read().splitlines()
            resolvers_file.close()
            logging.info(f"File: {resolvers} contains: {len(current)} DNS resolvers")

    except FileNotFoundError as e:
        logging.error(f"Error: Check your resolvers.txt file exists: {e}")
        exit()

    return len(current)


# Launch dnsvalidator to create a new list of dns resolvers
def get_new_list(executable, threads):

    try:
        with open(TEMP_FILE, "w") as temp_file:
            subprocess.run(f"{executable[0]} -threads {threads} --silent --no-color",
                           shell=True, stdout=temp_file, stderr=subprocess.DEVNULL)
        temp_file.close()

    except subprocess.CalledProcessError as e:
        logging.error(f"Error: Failed to launch dnsvalidator: {e}")
        exit()

    return None


# Launch dnsvalidator to validate domain resolvers in our existing list
def validate_current_list(executable, resolvers_file, threads):

    try:
        with open(TEMP_FILE, "w") as temp_file:
            subprocess.run(f"{executable[0]} -tL {resolvers_file} -threads {threads} --silent --no-color",
                           shell=True, stdout=temp_file, stderr=subprocess.DEVNULL)
            temp_file.close()

    except subprocess.CalledProcessError as e:
        logging.error(f"Error: Failed to launch dnsvalidator: {e}")
        exit()

    return None


# Remove original file, Move temp file to original and Remove the temporary file
def replace_file(resolvers_file):

    try:
        subprocess.run(["rm", "-r", resolvers_file], shell=False, capture_output=False)
        subprocess.run(["mv", TEMP_FILE, resolvers_file], shell=False, capture_output=False)

    except subprocess.CalledProcessError as e:
        logging.error(f"Error: There was an issue replacing the original file: {e}")
        exit()

    return None


# Tie it all in together
def main():

    args = parser.parse_args()
    minimum_resolvers = int(args.minimum)
    resolvers_file = args.resolvers
    threads = int(args.threads)
    output_type = args.output
    log_file = args.logfile

    log_config = get_output_type(output_type, log_file)
    logging.config.dictConfig(log_config)

    logging.info("Application is starting")
    executable = check_dnsvalidator()
    num_resolvers_in_file = check_current_file(resolvers_file)

    # +5 Just incase some are poisoned and dropped whilst validating
    if num_resolvers_in_file < (minimum_resolvers + 5):
        logging.info("Retrieving a fresh list of DNS resolvers")
        get_new_list(executable, threads)

    else:
        logging.info("Validating the current list of DNS resolvers")
        validate_current_list(executable, resolvers_file, threads)

    replace_file(resolvers_file)
    check_current_file(resolvers_file)
    logging.info("Application completed")
    exit()


if __name__ == "__main__":

    try:
        main()

    except RuntimeError as err:
        logging.error(f"Error: Encountered an error while executing: {err}")
        exit()
