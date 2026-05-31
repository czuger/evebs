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
  ./ nuc150:/home/ced/python/evebs/
  
ssh nuc150 "cd /home/ced/python/evebs/docker// && bash set_secret_key.bash"
ssh nuc150 "cd /home/ced/python/evebs/docker// && bash create_network.sh"

ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose down"
ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose up -d --build"