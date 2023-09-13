
## cmx-python-exporter

The cmx-python-exporter is a tool that exposes CMX metrics for Prometheus. It allows you to monitor and collect data from CMX for further analysis and vizualization.

1. **Metric Collection:** The script interacts with CMX data in shared memory to gather performance and monitoring metrics related to CMX components.
2. **Data Formats:**
    - **Prometheus:** Metrics can be accessed in Prometheus format, making it easy to use with Prometheus monitoring and alerting systems.
    - **JSON:** Metrics can be retrieved in JSON format, which is suitable for further processing and integration with other systems or debugging. It offers format that closely matches underlying CMX data.
3. **Web Server:** The script sets up a simple HTTP server that listens on port 9976. It provides a basic web interface with links to the available endpoints for accessing metrics.
4. **Docker Support:** The project includes a `Dockerfile` for containerizing the cmx-python-exporter, making it easy to deploy and run in a containerized environment.

## Building

Building steps are listed in [Dockerfile](Dockerfile).

## Usage

```bash
./cmx-python-exporter.py
```

The exporter will start, and you can access the metrics using the provided endpoints.

## Endpoints

The cmx-python-exporter exposes the following endpoints:

- `/`: Provides a simple HTML page with links to other endpoints.
- `/json`: Returns metrics data in JSON format.
- `/metrics`: Returns metrics data in Prometheus format.

## Docker

You can also run the cmx-python-exporter in a Docker container. Use the provided Dockerfile to build the image and then run the container.

```bash
docker build -t cmx-python-exporter .
docker run -d -p 9976:9976 -v /dev/shm:/dev/shm cmx-python-exporter
```

Please note that the container needs to be run with a shared memory device mounted; otherwise, won't be able to access metrics from the host.
In Kubernetes, when running monitored app and exporter as sidecar in the same pod it is not required, as they will use the same shared memory.
