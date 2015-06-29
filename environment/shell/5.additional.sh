#/usr/bin/env sh
# Additional packages setup

# Start of Additional Packages Setup
echo 'Installing additional packages'
yum -y install python-devel >/dev/null
yum -y install python-pip >/dev/null

yum -y install python34u >/dev/null
yum -y install python34u-pip >/dev/null

yum -y install mysql-devel >/dev/null
echo 'Finished installing additional packages'
# End of Additional Packages Setup

# Start of JDK Setup
echo 'Installing JDK 1.8.0'
yum -y install java-1.8.0-openjdk >/dev/null

if [[ -f '/root/.bashrc' ]] && ! grep -q 'export JAVA_HOME="/usr/lib/jvm/jre-1.8.0-openjdk"' /root/.bashrc; then
    echo 'export JAVA_HOME="/usr/lib/jvm/jre-1.8.0-openjdk"' >> /root/.bashrc
fi
if [[ -f '/etc/profile' ]] && ! grep -q 'export JAVA_HOME="/usr/lib/jvm/jre-1.8.0-openjdk"' /etc/profile; then
    echo 'export JAVA_HOME="/usr/lib/jvm/jre-1.8.0-openjdk"' >> /etc/profile
fi
echo 'Finished installing JDK 1.8.0'
# End of JDK Setup

# Start of Maven Initial Setup
echo 'Adding Maven'
MAVEN='http://apache.uberglobalmirror.com/maven/maven-3/3.3.3/binaries/apache-maven-3.3.3-bin.tar.gz'
MAVEN_CACHE="${CACHE_FOLDER}/$(echo ${MAVEN} | awk -F/ '{print $NF}')"
MAVEN_DIR_NAME="$(echo ${MAVEN} | awk -F/ '{print $NF}' | awk -F- 'sub(FS $NF,x)')"

mkdir -p "$CACHE_FOLDER"
if [ ! -e "${MAVEN_CACHE}" ]; then
    wget "${MAVEN}" -O "${MAVEN_CACHE}"
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
