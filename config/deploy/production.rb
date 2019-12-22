server 'pw', roles: %w{app web db}

# set :unicorn_config_path, "#{deploy_to}/current/config/unicorn/#{fetch(:stage)}_#{fetch(:application)}.rb"
# set :unicorn_pid, "#{current_path}/tmp/pids/unicorn.pid"

set :deploy_to, "/var/www/eve_business_server"
set :keep_releases, 3

# before 'deploy:publishing', 'deploy:before_publish_tasks' do
#   on 'hw' do
#     # Centralized pids management
#     if test("[ ! -d #{deploy_to}/shared/pids ]")
#       # Si shared pids n'existe pas, alors on le cree
#       execute "mkdir #{deploy_to}/shared/pids"
#     end
#     execute "ln -nfs  #{deploy_to}/shared/pids #{release_path}/pids"
#
#     # Centralized bundeling management
#     if test("[ ! -d #{deploy_to}/shared/vendor ]")
#       # Si shared vendor n'existe pas, alors on le cree
#       execute "mkdir #{deploy_to}/shared/vendor"
#     end
#     execute "rm -rf #{release_path}/vendor/bundle"
#     execute "ln -nfs  #{deploy_to}/shared/vendor #{release_path}/vendor/bundle"
#     execute "cd #{release_path}; RAILS_ENV=production bundle install --path vendor/bundle"
#
#     # Centralized sqlite production database management
#     if test("[ ! -d #{deploy_to}/shared/db ]")
#       # Si shared vendor n'existe pas, alors on le cree
#       execute "mkdir #{deploy_to}/shared/db"
#     end
#     if test("[ ! -f #{deploy_to}/shared/db/production.sqlite3 ]")
#       execute "sqlite3 #{deploy_to}/shared/db/production.sqlite3 \"\""
#     end
#     execute "ln -nfs  #{deploy_to}/shared/db/production.db #{release_path}/db/production.sqlite3"
#     # Migration
#     execute "cd #{release_path}; RAILS_ENV=production bundle exec rake db:migrate"
#
#     # Assets precompilation
#     execute "cd #{release_path}; RAILS_ENV=production bundle exec rake assets:precompile"
#   end
# end
#
# # Before publishing
# after 'deploy:publishing', 'deploy:start_unicorn' do
#   on 'hw' do
#     # Stopping current unicorn daemon
#     if test("[ -f #{deploy_to}/shared/pids/unicorn.pid ]")
#       execute "kill `cat #{deploy_to}/shared/pids/unicorn.pid`"
#     end
#     # Should fix the SECRET_KEY_BASE issue
#     execute "cd #{release_path}; SECRET_KEY_BASE=`bundle exec rake secret` bundle exec unicorn_rails -D -c config/unicorn/production_eve_business_server.rb -E production"
#   end
# end