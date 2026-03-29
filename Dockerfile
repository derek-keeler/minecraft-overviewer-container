# To use this Docker image, make sure you set up the mounts properly.
#
# The Minecraft server files are expected at
#     /home/minecraft/server
#
# The Minecraft-Overviewer render will be output at
#     /home/minecraft/render

FROM mcr.microsoft.com/openjdk/jdk:21-ubuntu

# -------------------- #
# BUILD-TIME ARGUMENTS #
# -------------------- #

ARG GITHUB_REF
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

RUN apt-get update && \
    apt-get upgrade -y -q && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        jq \
        python3-dev python3-numpy python3-pil python3 \
        wget \
        optipng && \
    apt-get autoremove -y -q && \
    apt-get clean -y -q && \
    groupadd minecraft -g $GROUP_ID && \
    useradd -m minecraft -u $USER_ID -g $GROUP_ID && \
    mkdir -p /home/minecraft/render /home/minecraft/server && \
    git clone --depth=1 $GITHUB_REPOSITORY Minecraft-Overviewer && \
    cd Minecraft-Overviewer && \
    python3 setup.py build && \
    python3 setup.py install

WORKDIR /home/minecraft/

COPY config/config.py entrypoint.sh download_url.py /home/minecraft/
# Add some timestamps / build information into the image
RUN printf "GITHUB_REF=%s\nGITHUB_REPOSITORY=%s\nGITHUB_SHA=%s\nBUILD_DATE=$(date -u)\n" "$GITHUB_REF" "$GITHUB_REPOSITORY" "$GITHUB_SHA" > /home/minecraft/build-details.txt

RUN chown minecraft:minecraft -R /home/minecraft/

USER minecraft

CMD ["bash", "/home/minecraft/entrypoint.sh"]
