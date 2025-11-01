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

## Deploying