role :app, %w{webapp@hw}
role :web, %w{webapp@hw}
role :db,  %w{webapp@hw}

set :deploy_to, "/var/www/eve_business_server_staging"
set :keep_releases, 1

set :branch, 'add_version_number'

set :unicorn_config_path, "#{deploy_to}/current/config/unicorn/#{fetch(:stage)}_#{fetch(:application)}.rb"
set :unicorn_pid, "#{current_path}/tmp/pids/unicorn.pid"
