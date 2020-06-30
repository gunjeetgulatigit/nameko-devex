FROM continuumio/miniconda3
MAINTAINER gitricko


USER root

# Install the latest Docker CE binaries (if needed)
RUN apt-get update && \
    apt-get -y --no-install-recommends install apt-transport-https \
      build-essential jq net-tools \
      ca-certificates \
      curl \
      gnupg2 \
      software-properties-common && \
    curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo "$ID")/gpg > /tmp/dkey; apt-key add /tmp/dkey && \
    add-apt-repository \
      "deb [arch=amd64] https://download.docker.com/linux/$(. /etc/os-release; echo "$ID") \
      $(lsb_release -cs) \
      stable" && \
   apt-get update && \
   apt-get -y --no-install-recommends install docker-ce && \
   apt-get clean

# Update conda
RUN conda update conda

# cant use root to start postgres, use same user as jenkins
ARG user=devuser
ARG group=devuser
ARG uid=1000
ARG gid=1000
ARG DEVUSER_HOME=/var/devuser_home

# Jenkins is run with user `jenkins`, uid = 1000
# If you bind mount a volume from the host or a data container,
# ensure you use the same uid
# https://github.com/jenkinsci/docker/blob/master/Dockerfile-slim
RUN mkdir -p $DEVUSER_HOME \
  && chown ${uid}:${gid} $DEVUSER_HOME \
  && groupadd -g ${gid} ${group} \
  && useradd -d "$DEVUSER_HOME" -u ${uid} -g ${gid} -m -s /bin/bash ${user}

RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ${DEVUSER_HOME}/.bashrc \
  && echo "conda activate base" >> ${DEVUSER_HOME}/.bashrc

# Install following backing service in (base)
# RabbitMQ, Postgres, Reddis, MongoDB
RUN conda create -n rabbitmq rabbitmq-server=3.7.16 -c conda-forge
RUN conda create -n mongodb mongodb=4.0.3 -c conda-forge
RUN conda create -n postgres postgresql=12.2 -c anaconda
RUN conda create -n redis redis=5.0.3 -c anaconda
