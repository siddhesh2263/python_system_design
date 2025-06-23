# Python - Microservice Architecture using Kubernetes, RabbitMQ, MongoDB, and MySQL

Install the following:
1. Docker
2. kubectl
3. minikube
4. MySQL
5. Python

<br>

## Part 1 - Auth Service Code

### Set up virtual environment.

`pip install virtualenv`

Go to source directory, then run:
```
python -m venv venv
./venv/Scripts/activate
```

The auth service is going to have its own MySQL database.

`show databases;`

`mysql -u root -p < init.sql`

This SQL script creates a MySQL user, database, and table for storing user data. The script grants all privileges to the user and defines a user table with fields id, email, and password.

![alt text](https://github.com/siddhesh2263/python_system_design/blob/main/assets/002_sql_file.png?raw=true)

<br/>

The `auth_user` is used for accessing the `auth` database. The `user` table contains the user that will be used to access the `auth` service. They are 2 different users with different purpose.

**Why do we need the auth service?** The microservice architecture operates within the Kubernetes cluster. These services are not accessible to the external internet since they are internal services. Access to them is achieved through a gateway, which is connected to the auth service. When a user sends their username and password, the gateway forwards this information to the auth service, which checks the credentials against those in the database. If there is a match, the auth service returns a JWT to the user. This JWT is then used by the user to access the internal services through the gateway. The JWT ensures that the user is authorized to access these services. A JWT consists of a header, payload, and signature.

Regarding the difference between `0.0.0.0` and `localhost` (related to loopback address): If a request originates from outside, it won’t be accessible if the host is set to `localhost`, as it restricts access within the host itself. Setting the host to `0.0.0.0` ensures that external requests are accessible (acting as a kind of wildcard).

<br/>

The below image shows a server.py file in a Flask project, where the Flask app is connected to a MySQL database using environment variables. It utilizes the `flask_mysqldb` package to establish a MySQL connection.

![alt text](https://github.com/siddhesh2263/python_system_design/blob/main/assets/001_db_config.png?raw=true)

<br/>

The below image shows a login route in a Flask app that validates a user's credentials from a MySQL database. It checks the email and password from the user table. If the credentials are valid, a JWT is created and returned. Otherwise, it returns an "invalid credentials" error.

![alt text](https://github.com/siddhesh2263/python_system_design/blob/main/assets/003_login_route.png?raw=true)

<br/>

The image shows the `createJWT()` function in Python, which generates a JWT (JSON Web Token). The token contains user data (username), expiration time (exp), issue time (iat), and additional authorization (admin). The token is signed using a secret key and the HS256 algorithm.

![alt text](https://github.com/siddhesh2263/python_system_design/blob/main/assets/004_create_jwt.png?raw=true)

<br/>

The below image shows the `/validate` route in Flask that decodes and validates a JWT passed in the Authorization header. If the token is missing or invalid, it returns an authorization error. The JWT is decoded using the same secret key and algorithm used during its creation.

![alt text](https://github.com/siddhesh2263/python_system_design/blob/main/assets/005_validate_jwt.png?raw=true)

<br/>

The below command will copy all dependencies into the text file.
```
pip freeze > requirements.txt
```

The following version worked while building the Dockerfile:
```
python:3.10-bullseye
```

Command to build dockerfile:
```
docker build .
```

Create a new repository in Docker Hub, name it as `auth`. Then use the `docker tag` command to tag the created image with the auth repository.

Then do: `docker push siddhesh2263/auth:latest`

<br/>

The image shows the Docker Hub repository named `siddhesh2263/auth`, containing an `auth` microservice image tagged as `latest`. This image was recently pushed, ready for Kubernetes deployment.

![alt text](https://github.com/siddhesh2263/python_system_design/blob/main/assets/006_docker_auth_latest.png?raw=true)

<br/>

The image shows the Dockerfile setup for an `auth` microservice, based on `python:3.10-bullseye`. It installs necessary dependencies, sets up the app directory, installs Python packages, and exposes port 5000.

![alt text](https://github.com/siddhesh2263/python_system_design/blob/main/assets/007_docker_file.png?raw=true)

106