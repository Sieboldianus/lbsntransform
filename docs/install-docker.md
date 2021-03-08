# Docker

This is the recommended approach:  

- If you have Docker  
- and if you do not want to develop or make changes to lbsntransform.

You can use the latest Dockerimage to directly run lbsntransform in a container:

First, pull the image.
```bash
docker pull registry.gitlab.vgiscience.org/lbsn/lbsntransform:latest
docker tag registry.gitlab.vgiscience.org/lbsn/lbsntransform:latest lbsntransform
```

The run it.
```bash
docker run \
    --rm \
    lbsntransform \
    --version
```

!!! note
    Replace `--version` with the CLI commands for your use case.
    
Or, use the Dockerfile in `docker/Dockerfile` to build the image yourself.

```dockerfile
{!../docker/Dockerfile!}
```

Example:
```bash
docker build -t lbsntransform -f docker/Dockerfile .
docker run \
    --rm \
    lbsntransform \
    --version
```