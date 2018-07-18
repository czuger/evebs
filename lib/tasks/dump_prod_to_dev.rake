namespace :db do
  namespace :dump do
    namespace :production_to_dev do

      desc 'Dump full database from production to dev'
      task :full => :environment do

        use_local_pg_dump = true
        if File.exists?( '/tmp/production.dump' )
          puts 'There already is a local dump. Do you want to remove it and refresh the dump ? (y/n)'
          result = STDIN.gets.chomp
          use_local_pg_dump = false if result == 'y'
        end

        unless use_local_pg_dump
          puts 'No local dump, retrieving ...'
          `ssh hw [ -e /tmp/production.dump ]`

          launch_remote_pg_dump = true
          if $?.to_i == 0
            puts 'There already is a remote dump. Do you want to remove it and refresh the dump ? (y/n)'
            result = STDIN.gets.chomp
            launch_remote_pg_dump = false unless result == 'y'
          end

          if launch_remote_pg_dump # file exist
            # Dump and compress it
            puts 'Running pg_dump on remote environment.'
            `ssh hw pg_dump -Fc -n public -T "eve_market_history_archives" -U eve_business_server eve_business_server_production -f /tmp/production.dump`
          end
          # Get the remote file
          puts 'Retrieving remote dump'
          `scp hw:/tmp/production.dump /tmp/`
        end

        puts 'Dropping database'
        `dropdb eve_business_server_dev`

        puts 'Creating database'
        `createdb eve_business_server_dev`

        `psql eve_business_server_dev -c 'CREATE EXTENSION hstore;'`

        puts 'Inserting datas'
        `pg_restore --no-owner -d eve_business_server_dev -n public /tmp/production.dump`
      end

    end
  end
end