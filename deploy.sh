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