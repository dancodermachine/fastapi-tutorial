# Deploying
1. How to structure your project to make it ready for deployment by using environmnt variables to set the configuration options you need.
2. Managing dependencies properly with `pip`. 
3. Deployment.
## Setting and Using Environmnet Variables
We need to structure our application to enable reliable, fast, and secure deployments. One of the key things in this process is handling configuration variables: a database URL, and external API token, a debug flag, and so on. When handling those variables, it's necessary to handle them dynamically instead of hardcoding them into your source code.

Variables will likely be different in your local environment and in production. It is unsafe to write those values in your code. To solve this, we usually use **environment vairables**. Environment variables are values that aren't set in the program itself but in the whole operating system.

During deployment, we'll only have to make sure that we set the correct environment variables on the server. This way, we can easily change a value without redeploying the code and have several deployments of our application containing different configurations sharing the same source code. However, bear in mind that sensitive values that have been set in environment variables can still leak if you don't pay attention - for example, in log files or error stack traces.

To help us with this task, we'll use a very convenient feature of Pydantic: settings management. This allows us to structure and use our configuration variables as we do for any other data model. It even takes care of automatically retrieving of values from environment variables.

### Using a .env file
In local deployment, it's a bit annoying to set environment variables by hand, especially if you're working on several projects at the same time and your machine. To solve this, Pydantic allows you to read the values from a .env file. This file contains a simple list of environments variables and their associated values. It's usually easier to edit and manipulate during development.

`pip install python-dotenv`

Ensure you don't commit this file by accident, it's usually recommended that you add it to your `.gitignore` file.

`touch .env`
## Managing Python Dependencies
When deploying a project to a new environment, such as a production server, we have to make sure all those dependencies are installed for our application to work properly. This is also true if you have colleagues that also need to work on the project: they need to know the dependencies they must install on their machines.

`requirements.txt` file, which contains a list of all Python dependencies.

The result of `pip freeze` is a list of every Python package currently installed in your environment, along with thier corresponding versions. This list can be directly used in the `requirements.txt` file. The problem with this approach is that it lists every package, including the sub-dependencies of the libraries you install.

To solve this, some people recommend that you manually maintain your `requirements.txt` file. With this approach, you have to list yourself all the libraries to use, along with thier respective versions.

During installation, `pip` will take care of installing the sub-dependencies, but they'll never appear in `requirements.txt`. This way, when you remove one of your dependencies, you make sure any useless packages are no kept.

The `requirements.txt` file should be committed along with your source code. When you need to install the dependencies on a new computer or server, you'll simply nned to run this command: `pip install -r requirements.txt`

### Gunicorn
ASGI sucessor of WSGI, provides a protocol for developing web servers running asynchronously. This protocol is at the heart of FastAPI and Starlette.

We us `Uvicorn` to run our FastAPI applications: it's role is to accept HTTP requests, transform them according to the ASGI protocol, and pass them to the FastAPI application, which returns an ASGI-compliant response object. Then, `Uvicorn` can perform a proper HTTP response from this object.

`Gunicorn` has lots of refinements and features that make it more robust and reliable in production than `Uvicorn`. However, `Gunicorn` is designed to work for WSGI applications.

Therefore, we use both: `Gunicorn` will be used as a robust process manager for our production server. However, we'll specify a special worker class provided by `Uvicorn`, which will allos us to run ASGI applications such as FastAPI.

`pip install gunicorn`

`gunicorn -w 4 -k uvicorn.workers.UvicornWorker project.app:app`

`w` allows us to set the number of workers to launch for our server. Then, `Gunicorn` takes care of load-balancing the incoming requests between each worker. This is what makes `Gunicorn` more robust: if, for any reason, your application blocks the event loop with a synchronous operation, other workers will be able to process other requests wile this is happening.

## Deploying Serverless
* Google App Engine
* Heroku
* Azure App Service

Serverless platforms expect you to provide the source code in the form of a GitHub repository, which you push directly to their servers or which they pull automatically from GitHub.

1. Create account.
2. Install the necessary command-line tools.
    - [Google](https://cloud.google.com/sdk/gcloud)
    - [Azure](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
    - [Heroku](https://devcenter.heroku.com/articles/heroku-cli)
3. Create configuration file or use the CLI or the web interface.
    - [Google](https://cloud.google.com/appengine/docs/flexible/python/configuring-your-app-with-app-yaml)
    - [Azure](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=fastapi)
    - [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python#define-a-procfile)
4. Set the environment variables.
    - [Google](https://docs.cloud.google.com/appengine/docs/legacy/standard/python/config/appref)
    - [Azure](https://learn.microsoft.com/en-us/azure/app-service/configure-common?tabs=portal#confiugre-app-settings)
    - [Heroku](https://devcenter.heroku.com/articles/config-vars)
5. Deploy.
    - [Google](https://docs.cloud.google.com/appengine/docs/standard/testing-and-deploying-your-app?tab=python)
    - [Azure](https://learn.microsoft.com/en-us/azure/app-service/deploy-continuous-deployment?tabs=github)
    - [Heroku](https://devcenter.heroku.com/articles/github-integration)
6. Add your domain
    - [Google](https://cloud.google.com/appengine/docs/flexible/mapping-custom-domains)
    - [Azure](https://learn.microsoft.com/en-us/azure/app-service/manage-custom-dns-migrate-domain)
    - [Heroku](https://devcenter.heroku.com/articles/custom-domains)
7. Adding database
    - [Google](https://docs.cloud.google.com/solutions/setting-up-cloud-sql-for-postgresql-for-production)
    - [Azure](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/quickstart-create-server?tabs=portal-create-flexible%2Cportal-get-connection%2Cportal-delete-resources)
    - [Heroku](https://www.heroku.com/postgres/)

Serverless platforms are the quickest and easiest way to deloy a FastAPI application.

## Deploying Docker
**Containers** are small, self-contained systems running on a computer. Each container contains all the files and configurations necessary for running a single application: a web server, a database engine, a data processing application, and so on. The main goal is to be able to run those applications without worrying about the dependency and version conflicts that often happen when trying to install and configure them on the system.

Docker containers are designed to be *portable and reproducible*: to create a Docker container, you simple have to write a **Dockerfile** containing all the necessary instructions to build the small system, along with all the files and configuration you need. Those instructions are executed during a **build**, which results in a Docker **image**. This image is a package containing your small system, ready to use, which you can easily share on the internet through **registries**. Any developer who has a working Docker installation can then download this image and run iton their system in a container.

### 1. Writing a Dockerfile
```
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

ENV APP_MODULE project.app:app

COPY requirements.txt /app

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

COPY ./ /app
```

Docker images are built using layers: each instruction will create a new layer in the build system. To improve performance, Docker does it best to reuse layers it has already built. Therefore, if it detects no changes from the previous build, it'll reuse the ones it has in memory without rebuilding them. By copying the `requirements.txt` file alone and installing the Python dependencies before the rest of the source code, we allow Docker to reuse the layer where the dependencies have been installed. If we edit out source code but not `requirements.txt`, the Docker build will only execute the last `COPY` instruction, reusing all the previous layers. Thus, the image is built in a few seconds instead of minutes.

### 2. Addint a Prestart Script
When deploying an application, it's quite common to run several commands before the application starts. The most typical case is to execute database migrations so that our production database has the correct set of tables and columns. To help us with this, our base Docker image allows us to create a bash script named `prestart.sh`
```
#! /usr/bin/env bash

# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head
```

### 3. Building a Docker Image
The dot (.) denotes the path of the root context to build your image - in this case, the current directory. The `-t` option is here to tag the image and give it a practical name.
```
docker build -t fastapi-app
```

### 4. Running a Docker Image Locally
```
docker run -p 8000:80 -e ENVIRONMENT=production -e DATABASE_URL=sqlite+aiosqlite:///app.db fastapi-app
```
* `-p` allows you to publish ports on your local machine.
* `-e` is used to set environment variables.

### 5. Deploying
* Google:
    - [Upload](https://docs.cloud.google.com/artifact-registry/docs/docker/store-docker-container-images)
    - [Deploy](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-fastapi-service)
* Azure:
    - [Upload](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli?tabs=azure-cli)
    - [Deploy](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-quickstart-portal)

## Conclusion
If you're not an experienced system administrator, we recommend that you favor serverless platforms; professional teams handle security, system updates, and server scalability for you, letting you focus on what matters most to you: developing a great application!