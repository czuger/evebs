# config valid only for Capistrano 3.4
lock '3.4.0'

set :application, 'eve_business_server'
set :repo_url, 'git:/opt/git/eve_business_server'

# Default branch is :master
# ask :branch, proc { `git rev-parse --abbrev-ref HEAD`.chomp }

# Default deploy_to directory is /var/www/my_app
set :deploy_to, "/var/www/eve_business_server"
set :keep_releases, 2

set :linked_dirs, fetch(:linked_dirs, []).push('log', 'tmp/pids', 'tmp/cache', 'tmp/sockets', 'vendor/bundle', 'public/system', 'public/uploads')
set :linked_files, fetch(:linked_files, []).push('config/database.yml', 'config/secrets.yml', 'db/eve.db' )

namespace :deploy do

  task :custom_restart do
    puts 'About to stop unicorn'
    invoke 'unicorn:stop'
    sleep( 1 ) # To give unicorn the time to really stop
    puts 'About to start unicorn'
    invoke 'unicorn:start'
    puts 'End starting unicorn'
  end

  task :update_version_number do
    on roles( :app ) do
      execute( "sed -i \"s/CHANGE_TO_VERSION_NUMBER/`wc -l #{fetch(:deploy_to)}/revisions.log | awk '{ print $1 }'`/g\" #{fetch(:release_path)}/app/views/layouts/_menu.html.haml" )
    end
  end

end

after 'deploy:publishing', 'deploy:update_version_number'
after 'deploy:publishing', 'deploy:custom_restart'

# Default branch is :master
# ask :branch, proc { `git rev-parse --abbrev-ref HEAD`.chomp }

# Default deploy_to directory is /var/www/my_app
# set :deploy_to, '/var/www/my_app'

# Default value for :scm is :git
# set :scm, :git

# Default value for :format is :pretty
# set :format, :pretty

# Default value for :log_level is :debug
# set :log_level, :debug

# Default value for :pty is false
# set :pty, true

# Default value for :linked_files is []
# set :linked_files, %w{config/database.yml}

# Default value for linked_dirs is []
# set :linked_dirs, %w{bin log tmp/pids tmp/cache tmp/sockets vendor/bundle public/system}

# Default value for default_env is {}
# set :default_env, { path: "/opt/ruby/bin:$PATH" }

# Default value for keep_releases is 5

