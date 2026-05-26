rsync -avz --progress \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='*.pyd' \
  --exclude='.Python' \
  --exclude='*.so' \
  --exclude='.pytest_cache/' \
  --exclude='*.egg-info/' \
  --exclude='build/' \
  --exclude='dist/' \
  --exclude='.idea/' \
  --exclude='.git/' \
  --exclude='databases' \
  --exclude='config.json' \
  --exclude='old' \
  ./ nuc150:/home/ced/python/twit/

ssh nuc150 "cd /home/ced/python/twit/docker// && bash set_secret_key.bash"
ssh nuc150 "cd /home/ced/python/twit/docker// && bash create_network.sh"

scp requirements.txt nuc150:/home/ced/python/twit/docker/

ssh nuc150 "cd /home/ced/python/twit/docker/ && docker compose down"
ssh nuc150 "cd /home/ced/python/twit/docker/ && docker compose up app-twitter -d"
ssh nuc150 "cd /home/ced/python/twit/docker/ && docker compose up app-twitter-post-daemon -d"