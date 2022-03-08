# Dev Docs

All commands are assumed to be run from the top level directory of this repository.

## Updating the Tiled Image Deployed on Spin

1) Make sure you have the latest tiled base image: `docker pull ghcr.io/bluesky/tiled:main`
2) Make local changes to the code
3) Build the image locally: `docker build -t harbor.nersc.gov/m3792/aimmdb:dev -f deploy/spin/docker/tiled/Dockerfile .`
4) Push the image to the nersc registry: `docker image push harbor.nersc.gov/m3792/aimmdb:dev`
5) Redeploy the tiled service on spin

## Updating the Tiled Config Deployed on Spin

The tiled service gets its configuration from `/global/project/projectdirs/m3792/aimm/config/config.yml` on the NERSC cfs.
By convention this should be kept up to date with the `deploy/spin/config/config.yml` file in this repository.
After updating the configuration redeploy the tiled service on spin for the changes to go into effect.

## Run Tiled Locally

For development purposes it is often useful to run the tiled server locally.
To do this we must be able to connect to the mongodb instance on spin which holds all of the data.
We can do this by using ssh to create a tunnel from spin to our locally machine through cori. 
For example, to create a tunnel to the staging server run `ssh -L localhost:27017:mongodb-loadbalancer.aimm-staging.development.svc.spin.nersc.org:27017 cori`.
Next set `MONGO_URI` to `mongodb://localhost:27017/aimm?authSource=admin` and `MONGO_PASSWORD` to the mongodb password.
These environment variables are used to inject the information for connecting to the database into the configuration.
Now we can start tiled using the locally configuration in this repo: `tiled serve config deploy/local/config.yml`
