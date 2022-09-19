FROM --platform=linux/amd64 centos/devtoolset-7-toolchain-centos7 as devcontainer
USER 0
RUN yum install -y --setopt=tsflags=nodocs epel-release && yum install -y --setopt=tsflags=nodocs git boost-devel cmake valgrind doxygen librdkafka-devel gtest cppcheck libtool autoconf python-devel && yum clean all -y
COPY .devcontainer/3rdparty /tmp/3rdparty
RUN cd /tmp/3rdparty/cmw-cmx && autoreconf --force --install && ./configure && make && make install
RUN export PKG_CONFIG_PATH="/tmp/3rdparty/cmw-cmx" \
&& export PYTHONPATH="$PYTHONPATH:/usr/local/lib/python2.7/site-packages/cmx-python:/usr/local/lib64/python2.7/site-packages/cmx-python" \
&& export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib:/usr/lib:/usr/lib64" \
&& cd /tmp/3rdparty/cmw-cmx-python && autoreconf --force --install && ./configure && make && make install

USER 1001

FROM --platform=linux/amd64 centos:centos7 as run
COPY --from=devcontainer /usr/local/ /usr/local/
COPY --from=devcontainer /usr/lib64/ /usr/lib64/ 
COPY src/cmx-python-exporter.py ./cmx-python-exporter.py
ENV \
PKG_CONFIG_PATH="/tmp/3rdparty/cmw-cmx" \
PYTHONPATH="$PYTHONPATH:/usr/local/lib/python2.7/site-packages/cmx-python:/usr/local/lib64/python2.7/site-packages/cmx-python" \
LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib:/usr/lib:/usr/lib64"
CMD ["./cmx-python-exporter.py"]
