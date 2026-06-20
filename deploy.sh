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
  --exclude='*.json' \
  --exclude='*.yaml' \
  --exclude='*.log' \
  --exclude='*.log.*' \
  --exclude='old' \
  ./ nuc150:/home/ced/python/evebs/
  
ssh nuc150 "cd /home/ced/python/evebs/docker// && bash set_secret_key.bash"
ssh nuc150 "cd /home/ced/python/evebs/docker// && bash create_network.sh"

# The compose project was renamed app-eve-dominion -> app-eve; tear down the old project so
# its now-orphaned containers (app-eve-dominion, app-eve-dominion-por) are removed.
ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose down app-eve --remove-orphans"
ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose up app-eve -d --build --remove-orphans"

# Recreating app-twitter gives it a new IP; nginx caches the old upstream IP, so reload
# it to re-resolve (otherwise /twitter/ returns "Host is unreachable" until next reload).
ssh nuc150 "docker exec nginx-proxy nginx -s reload"