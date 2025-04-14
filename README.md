# EEG monitor
This is a simple compose project that receives EEG data from a LSL stream (type==eeg), writes that into a TimescaleDB database, which is then queried by Grafana to show the data feed live in a dashboard.

## How to run
- Run `docker-compose up` to start the services.
- Open your browser and go to `http://localhost:3000` to access Grafana.
  - If you want to edit the dashboard, you can log in with the admin user `admin` and password `admin`.

## Caveats
- This setup does not work using rootless Docker as the LSL stream is discovered using multicast, which is not trivially supported in rootless Docker.
- Timescale is configured to only keep a short window of data, so this setup should theoretically run forever.