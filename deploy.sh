RESTART_DAEMON=false
for arg in "$@"; do
  case $arg in
    -d|--daemon) RESTART_DAEMON=true ;;
  esac
done

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

ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose down app-eve-dominion "
ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose up app-eve-dominion -d --build"
if [ "$RESTART_DAEMON" = true ]; then
  ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose down app-eve-dominion-public-orders-daemon-downloader"
  ssh nuc150 "cd /home/ced/python/evebs/docker/ && docker compose up app-eve-dominion-public-orders-daemon-downloader -d --build"
fi