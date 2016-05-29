#/usr/bin/env sh
# Additional packages setup

export DEBIAN_FRONTEND=noninteractive
BUILD_FOLDER=/build
CACHE_FOLDER=/environment/cache/packages

# Start of Additional Packages Setup
echo 'Installing additional packages'
apt-get install -y python python-dev python-pip >/dev/null

apt-get install -y python3 python3-dev python3-pip >/dev/null

apt-get install -y autoconf automake libtool >/dev/null

apt-get install -y libjansson4 libjansson-dev >/dev/null

apt-get install -y lua5.2 liblua5.2-dev >/dev/null

apt-get install -y libxslt-dev >/dev/null

apt-get install -y libmysqld-dev >/dev/null

apt-get install -y rrdtool >/dev/null

apt-get install -y gcc >/dev/null

apt-get install -y cmake >/dev/null

apt-get install -y flex >/dev/null
echo 'Finished installing additional packages'
# End of Additional Packages Setup

# Start of JDK Setup
echo 'Installing JDK 1.7.0'
apt-get install -y openjdk-7-jre openjdk-7-jdk

if [[ -f '/root/.bashrc' ]] && ! grep -q 'export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-i386"' /root/.bashrc; then
    echo 'export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-i386"' >> /root/.bashrc
fi
if [[ -f '/etc/profile' ]] && ! grep -q 'export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-i386"' /etc/profile; then
    echo 'export JAVA_HOME="/usr/lib/jvm/java-7-openjdk-i386"' >> /etc/profile
fi
echo 'Finished installing JDK 1.7.0'
# End of JDK Setup

# Start of Maven Initial Setup
echo 'Adding Maven'
MAVEN='http://apache.uberglobalmirror.com/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz'
MAVEN_CACHE="${CACHE_FOLDER}/$(echo ${MAVEN} | awk -F/ '{print $NF}')"
MAVEN_DIR_NAME="$(echo ${MAVEN} | awk -F/ '{print $NF}' | awk -F- 'sub(FS $NF,x)')"

mkdir -p "$CACHE_FOLDER"
if [ ! -e "${MAVEN_CACHE}" ]; then
    wget "${MAVEN}" -O "${MAVEN_CACHE}" >/dev/null
fi

mkdir -p "/tmp/maven"
cd /tmp/maven
tar -xzf "$MAVEN_CACHE"
cp -R "$MAVEN_DIR_NAME" /usr/local/maven

if [[ -f '/root/.bashrc' ]] && ! grep -q 'export PATH="$PATH:/usr/local/maven/bin"' /root/.bashrc; then
    echo 'export PATH="$PATH:/usr/local/maven/bin"' >> /root/.bashrc
fi
if [[ -f '/etc/profile' ]] && ! grep -q 'export PATH="$PATH:/usr/local/maven/bin"' /etc/profile; then
    echo 'export PATH="$PATH:/usr/local/maven/bin"' >> /etc/profile
fi

if [[ -f '/root/.bashrc' ]] && ! grep -q 'export M2_HOME="/usr/local/maven"' /root/.bashrc; then
    echo 'export M2_HOME="/usr/local/maven"' >> /root/.bashrc
fi
if [[ -f '/etc/profile' ]] && ! grep -q 'export M2_HOME="/usr/local/maven"' /etc/profile; then
    echo 'export M2_HOME="/usr/local/maven"' >> /etc/profile
fi
echo 'Finished adding Maven'
# End of Maven Initial Setup <<<
