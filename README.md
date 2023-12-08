# Technical Phishing Test Reports (TPT Reports) #

[![GitHub Build Status](https://github.com/cisagov/tpt-reports/workflows/build/badge.svg)](https://github.com/cisagov/tpt-reports/actions)
[![CodeQL](https://github.com/cisagov/tpt-reports/workflows/CodeQL/badge.svg)](https://github.com/cisagov/tpt-reports/actions/workflows/codeql-analysis.yml)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/tpt-reports/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/tpt-reports?branch=develop)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/tpt-reports/develop/badge.svg)](https://snyk.io/test/github/cisagov/tpt-reports)

This package is used to generate and deliver CISA Technical Phishing Test (TPT)
Reports. Reports are delivered locally and include an encrypted PDF attachment.
The package collects raw data and creates an encrypted PDF.

## Requirements ##

- [Python Environment](CONTRIBUTING.md#creating-the-python-virtual-environment)

## Installation ##

- These are the one time set up commands.

```console
git clone https://github.com/cisagov/tpt-reports.git
cd tpt-reports
./setup-env
pip install -e .
```

- Retrieve periodic project updates with these commands.

```console
git pull
pip install -e .
```

## Running the Project ##

- The output of the command `tpt-reports -h` provides usage details.

```console
Usage:
  tpt-reports ELECTION_NAME DOMAIN_TESTED JSON_FILE_PATH [--log-level=LEVEL] [--output-dir=OUTPUT_DIRECTORY]

Options:
  -h --help                         Show this message.
  -l --log-level=LEVEL              If specified, then the log level will be set to
                                    the specified value.  Valid values are "debug", "info",
                                    "warning", "error", and "critical". [default: info]
  -o --output-dir=OUTPUT_DIRECTORY  The directory where the final PDF reports
                                    should be saved. [default: ~/]

Arguments:
  ELECTION_NAME                     The name of the election being reported on.
  DOMAIN_TESTED                     The email domain used in the testing.
  JSON_FILE_PATH                    Path to the JSON file to act as a data source.
```

- Below is a sample command to create a report.

```console
tpt-reports "ABC Organization" domain.gov /filepath/data.json --output-dir=reports
```

## Contributing ##

We welcome contributions!  Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
details.

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
