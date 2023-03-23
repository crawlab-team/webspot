# Webspot

Webspot is an intelligent web service to automatically detect web content and extract information from it.

## Installation

Installation of Webspot is easy. Webspot is available on PyPI and can be installed using pip.

```bash
pip install webspot
```

## Usage

Webspot is a command line tool. It can be used to detect web content and extract information from it.

### Web UI

#### Start

Quick start by executing the command below.

```bash
webspot web
```

Then you can access the web UI at http://localhost:80.

#### Options

```bash
webspot web --help
```

## Architecture

### Overview

The overall process of how Webspot detects meaningful elements from HTML or web pages is shown in the following figure.

```mermaid
graph LR
    hr[HtmlRequester]
    gl[GraphLoader]
    d[Detector]
    r[Results]

    hr --"html + json"--> gl --"graph"--> d --"output"--> r
```

## Development

Development with Webspot is easy. You can follow the following guidance to get started.

### Pre-requisites

- Python >=3.8 and <=3.10
- Go 1.16 or higher
- MongoDB 4.2 or higher

### Install dependencies

```bash
# dependencies
pip install -r requirements.txt
```

### Start web server

```bash
# start development server
python main.py web
```

### Code Structure

The core code is located in `webspot` directory. The `main.py` file is the entry point of the web server.

```
webspot
├── cmd     # command line tools
├── crawler # web crawler
├── data    # data files (html, json, etc.)
├── db      # database
├── detect  # web content detection
├── graph   # graph module
├── models  # models
├── request # request helper
├── test    # test cases
├── utils   # utilities
└── web     # web server
```
