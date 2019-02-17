FROM ubuntu:trusty
RUN apt-get -y update && apt-get -y install xinetd vim net-tools gdbserver
RUN useradd -m rop1 && \
    useradd -m rop2 && \
    useradd -m rop3 && \
    chmod 700 /home/rop1 /home/rop2 /home/rop3 && \
    mkdir /app

# Otherwise reverse shells don't work nice.
RUN cp /bin/bash /bin/sh
COPY ./bin/motd_* /app/
COPY ./xinetd.conf /etc/xinetd.d/rop
COPY ./bin/1.txt /home/rop1/flag.txt
COPY ./bin/2.txt /home/rop2/flag.txt
COPY ./bin/3.txt /home/rop3/flag.txt

CMD ["/usr/sbin/xinetd", "-dontfork"]
