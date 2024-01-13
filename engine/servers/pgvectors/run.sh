docker run \
  --name pgvecto-rs-demo \
  --net=host \
  -v /mnt/disks/ssd0/pgdata:/var/lib/postgresql/data \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -e POSTGRES_PASSWORD=mysecretpassword \
  --memory-swap 0 \
  -d tensorchord/pgvecto-rs:pg16-v0.1.14-beta

python run.py --engines "*pgvectors*" --upload