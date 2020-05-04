## Overview
Funbox test task.

## Requirements
Python 3.7+, 
Redis4.0.1+

## Running with Docker Compose

!!! This usage highly recommended.

To run the server on a Docker containers, please execute the following from the root directory:

```bash
# building the image
docker-compose build 

# starting up a container
docker-compose up
```

## Usage
First set next environment variables:

```bash
export DATABASE_ENGINE=redis  # the only one options so far.
export DATABASE_HOST=localhost  # ip address of your db
export DATABASE_PORT  # db posrt
```

To run the server, please execute the following from the root directory:

```bash
cd server/
pip3 install -r requirements.txt
gunicorn -b localhost:8080 main:__hug_wsgi__
```

and open your browser to here:

```
http://localhost:8080/visited_domains
```

Testing based on inner hug testing system. To launch the integration tests

```bash
python37 test.py
```

