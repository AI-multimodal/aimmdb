# This doesn't work yet, but it's a start...the pod name is the name of deployment, not the actual pod

rancher kubectl exec postgres-backup -n aimm -- bash -c "pg_dump postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/tiled > /backup/database.sql"