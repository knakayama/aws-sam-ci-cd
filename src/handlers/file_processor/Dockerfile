FROM amazonlinux:2017.09.0.20170930

WORKDIR /workdir
COPY *.txt ./
RUN yum install -y gcc python36 python36-devel

ENTRYPOINT ["pip-3.6", "install", "-r", "requirements.txt", "-c", "constraints.txt", "-t", "./vendored"]
