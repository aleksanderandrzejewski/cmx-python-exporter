FROM --platform=linux/amd64 centos/devtoolset-7-toolchain-centos7 as devcontainer
USER 0
RUN yum install -y --setopt=tsflags=nodocs epel-release && yum install -y --setopt=tsflags=nodocs git boost-devel cmake valgrind doxygen librdkafka-devel gtest cppcheck libtool autoconf python-devel && yum clean all -y
COPY 3rdparty /tmp/3rdparty
RUN cd /tmp/3rdparty/cmw-cmx && autoreconf --force --install && ./configure && make && make install
RUN export PKG_CONFIG_PATH="/tmp/3rdparty/cmw-cmx" \
&& export PYTHONPATH="$PYTHONPATH:/usr/local/lib/python2.7/site-packages/cmx-python:/usr/local/lib64/python2.7/site-packages/cmx-python" \
&& export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib:/usr/lib:/usr/lib64" \
&& cd /tmp/3rdparty/cmw-cmx-python && autoreconf --force --install && ./configure && make && make install

USER 1001
