role :app, %w{webapp@hw}
role :web, %w{webapp@hw}
role :db,  %w{webapp@hw}

set :deploy_to, "/var/www/eve_business_server_staging"
set :keep_releases, 1

set :branch, 'master'

set :unicorn_config_path, "#{deploy_to}/current/config/unicorn/#{fetch(:stage)}_#{fetch(:application)}.rb"
set :unicorn_pid, "#{current_path}/tmp/pids/unicorn.pid"

after :deploy, :cleanup do
  on roles(:app) do
    execute 'ln -s /home/webapp/eve_business_server/caddie /var/www/eve_business_server_staging/releases/'
  end
end