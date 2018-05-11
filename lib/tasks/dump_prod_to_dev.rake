namespace :db do
  namespace :dump do
    namespace :production_to_dev do

      desc 'Dump full database from production to dev'
      task :full => :environment do

        unless File.exists?( '/tmp/production.dump' )
          puts 'No local dump, retrieving ...'
          `ssh hw [ -e /tmp/production.dump ]`
          unless $?.to_i == 0 # file exist
            # Dump and compress it
            puts 'No remote dump, pg_dump'
            `ssh hw pg_dump -Fc -n public -T "eve_market_history_archives" -U eve_business_server eve_business_server_production -f /tmp/production.dump`
          end
          # Get the remote file
          puts 'Retrieving remote dump'
          `scp hw:/tmp/production.dump /tmp/`
        end

        puts 'Dropping database'
        `dropdb eve_business_server_dev -U eve_business_server`

        puts 'Creating database'
        `createdb eve_business_server_dev -U eve_business_server -O eve_business_server`

        puts 'Inserting datas'
        `pg_restore -U eve_business_server -d eve_business_server_dev -n public /tmp/production.dump`
      end

    end
  end
end