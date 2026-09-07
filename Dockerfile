# To use this Docker image, make sure you set up the mounts properly.
#
# The Minecraft server files are expected at
#     /home/minecraft/server
#
# The Minecraft-Overviewer render will be output at
#     /home/minecraft/render

FROM python:3.14-slim-trixie

# -------------------- #
# BUILD-TIME ARGUMENTS #
# -------------------- #

ARG GITHUB_REF=main
ARG GITHUB_REPOSITORY="https://github.com/GregoryAM-SP/The-Minecraft-Overviewer.git"
ARG GITHUB_SHA
ARG USER_ID=1000
ARG GROUP_ID=1000

LABEL OriginalAuthor='Mark Ide Jr (https://www.mide.io)'
LABEL Maintainer="Derek Keeler <34773432+derek-keeler@users.noreply.github.com>"

# --------------- #
# OPTION DEFAULTS #
# --------------- #

# See README.md for description of these options
ENV CONFIG_LOCATION=/home/minecraft/config.py
ENV RENDER_MAP="true"
ENV RENDER_POI="true"
ENV RENDER_SIGNS_FILTER="-- RENDER --"
ENV RENDER_SIGNS_HIDE_FILTER="false"
ENV RENDER_SIGNS_JOINER="<br/>"

# ---------------------------- #
# INSTALL & CONFIGURE DEFAULTS #
# ---------------------------- #

WORKDIR /home/minecraft/

RUN apt-get update && apt-get upgrade -qq -y && apt-get install -y --no-install-recommends \
	gcc \
	build-essential \
	ca-certificates \
	curl \
	jq \
	wget \
	optipng \
	git \
	libjpeg-dev \
	zlib1g-dev \
	&& python3 -m pip install -qq -U pip setuptools \
        && curl -o jdk.tar.gz -L https://aka.ms/download-jdk/microsoft-jdk-25-linux-x64.tar.gz \
        && mkdir -p /usr/lib/jvm/msopenjdk-25 \
        && tar -xvzf jdk.tar.gz -C /usr/lib/jvm/msopenjdk-25 --strip-components 1 \
        && rm jdk.tar.gz \
        && for f in `find /usr/lib/jvm/msopenjdk-25/bin/ -type f -printf "%f\n"`; do update-alternatives --install /usr/bin/${f} ${f} /usr/lib/jvm/msopenjdk-25/bin/${f} 2082; done \
	&& git clone --depth=1 -b $GITHUB_REF $GITHUB_REPOSITORY Minecraft-Overviewer \
	&& cd Minecraft-Overviewer \
	&& git clone --branch=12.1.1 --depth=1 https://github.com/python-pillow/Pillow.git /tmp/pillow \
	&& PIL_INCLUDE_DIR=/tmp/pillow/src/libImaging pip install . \
	&& PIL_INCLUDE_DIR=/tmp/pillow/src/libImaging python3 setup.py build \
	&& apt-get autoremove -y -qq \
	&& apt-get clean -y -qq \
	&& groupadd minecraft -g $GROUP_ID \
	&& useradd minecraft -u $USER_ID -g $GROUP_ID \
	&& mkdir -p /home/minecraft/render /home/minecraft/server \
	&& rm -rf /tmp/pillow /var/lib/apt/lists/*

WORKDIR /home/minecraft/

COPY config/config.py entrypoint.sh download_url.py /home/minecraft/
# Add some timestamps / build information into the image
RUN printf "GITHUB_REF=%s\nGITHUB_REPOSITORY=%s\nGITHUB_SHA=%s\nBUILD_DATE=$(date -u)\n" "$GITHUB_REF" "$GITHUB_REPOSITORY" "$GITHUB_SHA" > /home/minecraft/build-details.txt

RUN chown minecraft:minecraft -R /home/minecraft/

USER minecraft

CMD ["bash", "/home/minecraft/entrypoint.sh"]
