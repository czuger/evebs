server 'dw', roles: %w{app web db}

# set :unicorn_config_path, "#{deploy_to}/current/config/unicorn/#{fetch(:stage)}_#{fetch(:application)}.rb"
# set :unicorn_pid, "#{current_path}/tmp/pids/unicorn.pid"

set :keep_releases, 1
set :deploy_to, "/var/www/eve_business_server_staging"