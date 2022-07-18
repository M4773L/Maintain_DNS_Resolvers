# Maintain DNS Resolvers
This is a simple application to leverage the functionality of [dnsvalidator](https://github.com/vortexau/dnsvalidator) to maintain a list of valid DNS resolvers. Intended to be 
run as a cron job, the program will read the file containing the DNS resolvers into a list, if the length of the list is less than the minimum
number of resolvers you have defined, the script will run dnsvalidator and create a new file of resolvers. 
If the length of the list is greater than the minimum number of resolvers, the script will run dnsvalidator and validate your existing 
list of resolvers. The output from the program can be to either the console or a log file which can be configured by command line argument or via constant value in the code.  

The application uses only native Python3 packages and only requires that [dnsvalidator](https://github.com/vortexau/dnsvalidator) is installed and in your current users $PATH. 

## Options
The application has been designed so that arguments can be supplied via the command line or the application will default to constant values.
It can be executed with only some flags and those not supplied will simply default to the constants. 
The program will default to the scripts location as the work directory.

#### Command Line
By launching the application with command line arguments, the constant values will be overidden by the supplied arguments.
```
┌──(m477㉿kali)-[~/Tools/Maintain_DNS_Resolvers]
└─$ python3 maintain_resolvers.py -h          
usage: maintain_resolvers.py [-h] [-m MINIMUM] [-r RESOLVERS] [-t THREADS] [-l LOGFILE] [-o OUTPUT]

Manage a list of reliable domain resolvers using DNSValidator

options:
  -h, --help            show this help message and exit
  -m MINIMUM, --minimum MINIMUM
                        Minimum number of resolvers in file
  -r RESOLVERS, --resolvers RESOLVERS
                        File containing resolvers to check
  -t THREADS, --threads THREADS
                        Number of threads to use for dnsvalidator
  -l LOGFILE, --logfile LOGFILE
                        Path to logfile
  -o OUTPUT, --output OUTPUT
                        How to handle this programs output - options = 'log' or 'console'
```
The help screen displayed by executing the program with the '-h' flag.

#### Constant Values
By changing the values of these constants you remove the need to supply any additional arguments at time of execution.
```
# The program will default to these values unless executed with arguments from the terminal
# Default values
MINIMUM_RESOLVERS = 100
WORK_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
RESOLVERS_FILE = os.path.join(WORK_DIRECTORY, "resolvers.txt")
TEMP_FILE = os.path.join(WORK_DIRECTORY, "resolvers.tmp")
LOG_FILE = os.path.join(WORK_DIRECTORY, "app.log")
DEFAULT_OUTPUT_METHOD = "CONSOLE"  # Options: 'CONSOLE' or 'LOG'
THREADS = 5
```

For example; 
To change the location of the file containing resolvers
```
RESOLVERS_FILE = os.path.join("/home/m477/resources", "resolvers.txt")
```
Replace 'WORK_DIRECTORY' with the full path to the directory, be sure you have appropriate write permissions to the directory.  

To enable logging to file by default
```
DEFAULT_OUTPUT_METHOD = "LOG"  # Options: 'CONSOLE' or 'LOG'
```
Simply change the value from 'CONSOLE' to 'LOG'

## Running maintain_resolvers.py
The program requires [dnsvalidator](https://github.com/vortexau/dnsvalidator) to be installed and in your current users $PATH, the program also requires that a file for the 
resolvers actually exists. Please either run [dnsvalidator](https://github.com/vortexau/dnsvalidator) and output to a file OR simply create an empty file and either update the 
constants or execute with appropriate command line arguments.

#### Using Constants
```
┌──(m477㉿kali)-[~/Tools/Maintain_DNS_Resolvers]
└─$ python3 maintain_resolvers.py
```
Will run the program with the constant values used as the applications arguments.

#### With Command Line Arguments
```
┌──(m477㉿kali)-[~/Tools/Maintain_DNS_Resolvers]
└─$ python3 maintain_resolvers.py -minimum 100 -threads 10  -o console
```
Will run the program using the arguments supplied via the command line and will default to the constant values for arguments that are not supplied.

For example;
Short Arguments
```
┌──(m477㉿kali)-[~/Tools/Test_Updater]
└─$ python3 maintain_resolvers.py -m 175 -r /path/to/file.txt -t 10 -o log -l /path/to/file.log 
```

Long Arguments
```
┌──(m477㉿kali)-[~/Tools/Test_Updater]
└─$ python3 maintain_resolvers.py --minimum 175 --resolvers /path/to/file.txt --threads 10 --output log --logfile /path/to/file.log
```
Both of these examples will execute the program to maintain a minimum of 175 resolvers in the file named 'file.txt', there will be 10 threads
used by dnsvalidator, the programs output will be directed to a log file named 'file.log'.

#### Cron
```
15 */4 * * * python3 /home/Tools/Maintain_DNS_Resolvers/maintain_resolvers.py > /dev/null 2>&1
```
This example will run at 15 minutes past every 4th hour with any output redirected to '/dev/null'. When running by crontab I recommend 
changing the constant values to tune the application to your liking.

## Other Notes...

#### Log File
The program uses the RotatingFileHandler module from the logging package, currently the configuration has a log file size of 1MB and a 
backupCount of 1. Meaning that when the log file reaches 1MB it will have '.1' appended to the filename and will start with a fresh file, when the process is repeated for a second time the file that was '.1' will be discarded. 
```
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

```
This may be changed if you desire a different logging configuration.

Example log file output;
```
[19-07-2022 07:24:27] Application is starting
[19-07-2022 07:24:27] File: /home/m477/Tools/Maintain_DNS_Resolvers/resolvers.txt contains: 1027 DNS resolvers
[19-07-2022 07:24:27] Validating the current list of DNS resolvers
[19-07-2022 07:45:25] File: /home/m477/Tools/Maintain_DNS_Resolvers/resolvers.txt contains: 975 DNS resolvers
[19-07-2022 07:45:25] Application completed
```

#### Note to self:
I make these README files too detailed, hopefully someone finds something useful :)
