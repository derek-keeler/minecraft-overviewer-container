# Copilot instructions for this repository

## Commands

Use PowerShell commands for local development; do not assume `make` is available on the primary dev platform.

- Build the local image:

  ```powershell
  docker build -t mide/minecraft-overviewer:latest -f Dockerfile .
  ```

- Build the Minecraft 26.1 Overviewer update branch:

  ```powershell
  docker build -t mide/minecraft-overviewer:mc-26.1 -f Dockerfile --build-arg GITHUB_REF=dek/handle-mc-26.1 --build-arg GITHUB_REPOSITORY=https://github.com/derek-keeler/The-Minecraft-Overviewer.git .
  ```

- Run the render smoke test:

  ```powershell
  git clone https://github.com/overviewer/Overviewer-Test-Data.git test-data
  Move-Item test-data\world_189 test-data\world
  docker run --rm -it -e MINECRAFT_VERSION="1.14.1" -v "${PWD}\test-data:/home/minecraft/server/:ro" -v "${PWD}\test-data-output:/home/minecraft/render/:rw" mide/minecraft-overviewer:latest
  ```

- Clean generated render test data:

  ```powershell
  Remove-Item -Recurse -Force test-data,test-data-output -ErrorAction SilentlyContinue
  ```

- Run lint locally with Super-Linter:

  ```powershell
  docker pull github/super-linter
  docker run --rm -e RUN_LOCAL=true -v "${PWD}:/tmp/lint" github/super-linter
  ```

- Inspect the image with Dive:

  ```powershell
  docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock -e CI=true wagoodman/dive:latest "mide/minecraft-overviewer:latest"
  ```

The repository still has equivalent Makefile targets for Unix-like environments, but future Copilot work should prefer the PowerShell forms above unless the user asks otherwise.

CI runs Super-Linter on every push and performs a multi-platform Docker Buildx build for `linux/amd64` and `linux/arm64`. The scheduled/push builder workflow pushes `mide/minecraft-overviewer:latest` to Docker Hub.

## Architecture

This repository packages The Minecraft Overviewer as a Docker image with a default runtime configuration:

- `Dockerfile` builds from `python:3.14-slim-trixie`, installs OS dependencies plus Microsoft OpenJDK, clones the Overviewer repository selected by `GITHUB_REPOSITORY` and `GITHUB_REF`, installs it with a pinned Pillow checkout, then copies this repo's runtime files into `/home/minecraft/`.
- `entrypoint.sh` is the container runtime coordinator. It requires `MINECRAFT_VERSION`, resolves `latest` and `latest_snapshot` through Mojang's manifest, downloads the matching client jar through `download_url.py` when it is not already mounted, then runs `overviewer.py` for map rendering and/or POI generation based on environment flags.
- `download_url.py` is consumed by `entrypoint.sh`; it reads `MANIFEST_URL` from the environment, validates HTTPS URLs, follows Mojang version metadata, and prints the Minecraft client jar URL.
- `config/config.py` is loaded by upstream Overviewer, not as a normal standalone Python module. It defines the world path, output directory, marker filters, render definitions, and sign/player POI behavior expected by Overviewer.

Runtime paths are part of the container contract: Minecraft server data is expected at `/home/minecraft/server/`, rendered output goes to `/home/minecraft/render/`, and the default Overviewer config path is `/home/minecraft/config.py`.

## Repository-specific conventions

- Use `https://github.com/derek-keeler/The-Minecraft-Overviewer.git` as the Overviewer source repository when building locally or wiring build arguments. Keep the Dockerfile's default `GITHUB_REF` on `main`; use `--build-arg GITHUB_REF=...` for feature branches such as `dek/handle-mc-26.1`.
- Do not shallow-clone the Overviewer source in `Dockerfile`; its setup code derives the package version from git tags and a shallow clone can produce `InvalidVersion: 'unknown'`.
- Install the pinned Pillow checkout before installing Overviewer so setup can detect the Pillow major version and compile the C extension against Pillow 12 headers.
- Keep user-facing runtime options synchronized between `Dockerfile` `ENV` defaults and `README.md` environment variable documentation.
- Preserve `entrypoint.sh`'s ability to pass multi-word `ADDITIONAL_ARGS` and `ADDITIONAL_ARGS_POI` through to `overviewer.py`; the existing ShellCheck suppressions are intentional for that behavior.
- Treat `config/config.py` as Overviewer configuration. Undefined names such as `worlds`, `renders`, `Base`, `EdgeLines`, and overlay classes are supplied by Overviewer at load time, so the file intentionally disables undefined-name lint/type warnings.
- Sign filtering supports both pre-1.20 sign fields (`Text1`-`Text4`) and 1.20+ `front_text`/`back_text` message structures; preserve both paths when changing POI rendering.
- Python scripts should have a top-level docstring explaining inputs, outputs, and the high-level transformation; substantial functions should also have docstrings.
- Docker build args `GITHUB_REF`, `GITHUB_REPOSITORY`, and `GITHUB_SHA` are written to `/home/minecraft/build-details.txt`, so keep those args wired through CI build workflows when changing image build metadata.
