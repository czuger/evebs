namespace :db do
  namespace :dump do
    namespace :prod_to_staging do

      desc 'Dump full database from prod to staging'
      task :full => :environment do

        `ssh hw [ -e /tmp/production.dump ]`
        unless $?.to_i == 0 # file exist
          puts 'Dump does not exist. Dumping'
          `ssh hw 'pg_dump -Fc -U eve_business_server -n public eve_business_server_production -f /tmp/production.dump'`
        end

        puts 'Stopping staging server'
        `cap staging unicorn:stop`

        puts 'Dropping database'
        `ssh hw 'dropdb eve_business_server_staging -U eve_business_server'`

        puts 'Creating database'
        `ssh hw 'createdb eve_business_server_staging -U eve_business_server -O eve_business_server'`

        puts 'Inserting datas'
        `ssh hw 'pg_restore -U eve_business_server -f eve_business_server_staging -n public /tmp/production.dump'`

        puts 'Starting staging server'
        `cap staging unicorn:start`
      end
    end
  end
end