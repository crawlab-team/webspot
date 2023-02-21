FROM golang:1.19 AS build

WORKDIR /go/src/app
COPY ./webspot_rod .

ENV GO111MODULE on

RUN go mod tidy \
  && go install -v ./...

FROM python:3.10.9

# Working directory
WORKDIR /app

# System info
RUN echo `uname -a`
RUN echo `python --version`

# Install supervisor
RUN apt-get update && apt-get install -y supervisor

# Start and enable SSH
RUN apt-get update \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "root:Docker!" | chpasswd \
    && chmod u+x ./entrypoint.sh
COPY webspot_rod/conf/sshd_config /etc/ssh/

# Expose SSH port
EXPOSE 8000 2222

# Copy webspot_rod
COPY --from=build /go/bin/webspot_rod /go/bin/webspot_rod
COPY webspot_rod/conf/supervisord.conf /etc/supervisor/supervisord.conf

# Install requirements
COPY ./requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install torch --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install dgl -f https://data.dgl.ai/wheels/repo.html

# Add source code
ADD . /app

# Expose port 80
# This is important in order for the Azure App Service to pick up the app
ENV PORT 80
EXPOSE 80

ENTRYPOINT ["entrypoint.sh"]
CMD ["web"]
