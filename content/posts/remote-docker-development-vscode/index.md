---
title: "Remote software development with VSCode and Docker Compose"
date: 2023-10-03T12:48:00+01:00
draft: false

tags:
- VSC
- Docker
- Docker Compose
- SSH
- Remote Development

cover:
    image: "cover.png"
    alt: "VSC Logo"

summary:
    Modern software development often requires us to juggle multiple services and environments. When you add the constraint of sensitive data or specific hardware requirements, this complexity can grow. Fortunately, tools like VSCode, Docker, and SSH are here to simplify our lives. In this post, we'll walk through setting up a development environment that leverages a virtual machine (VM) remotely, providing both security and flexibility.
---

Modern software development often requires us to juggle multiple services and environments. When you add the constraint of sensitive data or specific hardware requirements, this complexity can grow. Fortunately, tools like VSCode, Docker, and SSH are here to simplify our lives. In this post, we'll walk through setting up a development environment that leverages a virtual machine (VM) remotely, providing both security and flexibility.


## Our Guidepost: A Django Application

To better understand the concept, consider this example `docker-compose.yml` for a Django application, equipped with PostgreSQL as its database and Redis:

```yaml

`version: '3.8'

services:
  web:
    image: django:latest
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - app-data:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - cache

  db:
    image: postgres:latest
    environment:
      POSTGRES_DB: sampledb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - db-data:/var/lib/postgresql/data

  cache:
    image: redis
    command: redis-server --save 20 1 --loglevel warning

volumes:
  app-data:
  db-data:

```
This configuration offers a Django web service (`web`) that leans on PostgreSQL (`db`) for its data storage and Redis (`cache`) for caching. It illustrates a typical setup that many web applications could use.

## Why SSH 

A virtual machine, named `DevVM` for this story, could be running in a cloud service, a secluded private data center, or even on a local grid. Whether you're working on an on-premise SecureMachine or a cloud-based DevVM, SSH is the key. It provides a secure bridge to both, ensuring encrypted access to these remote resources.

## Containers and Docker Compose

Containers have become instrumental in the modern software ecosystem due to their promise of portability. With many services now leaning towards containerized deployments, technologies like Docker, a popular choice among developers, ensure that applications are consistently executed, regardless of where they're run. To further enhance this, tools like Docker Compose step in, allowing us to weave multiple containers into an interdependent stack. This makes booting up an entire software stack, with all its intricacies and dependencies, as straightforward as executing a single command.

## Setting Up with VSCode

Now with the introduction out of the way, lets start explaining how to setup all this. I assume you have the following:

### Prerequisites
-   SSH key for  your `DevVM` or `SecureMachine`
-   Docker installed on your local machine
-   Visual Studio Code (VSCode) with Docker extension installed on your local machine

### Step 1: Clone the Project

We clone our project repository to our local machine:

```bash
git clone git@github.com:YourUsername/YourRepo.git
```

### Step 2: Connect to `DevVM` using Docker and SSH

First, establish a Docker context for the VM:

```bash
docker context create DevVM --docker "host=ssh://user@DevVM:22"
```

In VSCode:

1. Open the Command Palette (`Ctrl + Shift + P`).
2. Type and select `Docker Contexts: Use`.
3. Choose the `DevVM` context.

### Step 3: Configure the Development Environment

In your project root, create a `.devcontainer` directory. Inside, add a `devcontainer.json`:

```json
{
   "name": "ProjectName",
   "dockerComposeFile": [
       "../docker-compose.yaml"
   ],
   "service": "web",
   "workspaceFolder": "/app/", 
   "overrideCommand": true
}
```
In this case I copied my Django project inside the folder /app when building my docker and therefore, I target this folder as the startup `workspaceFolder`. Note the `overrideCommand: true`. I added this to override the default command that is specified in the docker-compose file, to avoid the container from starting up the Django server. By doing this it will fall back to the default command specified in the Dockerfile, which is `CMD ["/bin/bash"]`. This will allow us to start the Django server manually for debugging purposes.

To ensure data persistence and easy access, introduce a volume, `app-data`, to your docker service. In the context of our setup, this volume I attached to the `web` service, making sure that when your docker fails you won't lose your uncommited changes. 

### Step 4: Engage in Development

In VSCode:

1. Open the Command Palette.
2. Search and select "Dev Containers: Reopen in Container." 
OR
3. Click on the green bottom left `><` button all the way in the corner.
4. Select "Reopen in Container"

VSCode will now set everything up, and you're all set to develop!

## For PyCharm Aficionados

I have to admit, I love PyCharm and I should definitely mention that it also supports connecting to Docker via SSH, allowing you to work seamlessly with your project using Docker Compose. However, when I tried this setup I had trouble setting up the Docker Compose interpreter via a remote ssh Docker service. Maybe this is a bug in the current 2023.2 or I'm doing something wrong. 

## For the solo developer

You could also install VSCode Studio Server and setup a tunnel so you connect with your local VSC to it. I think it will make the setup a bit more smoother and less complex, however I choose for this solution since I had to share my machine. With this solution multiple developers can run a docker-stack on the same machine. 

## Wrapping Up

Remote development doesn't have to be complex. With VSCode, Docker, and SSH, coupled with the power of VMs, developers can enjoy a flexible, secure, and consistent coding environment.