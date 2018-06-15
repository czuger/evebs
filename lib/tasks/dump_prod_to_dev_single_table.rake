namespace :db do
  namespace :dump do
    namespace :production_to_dev do

      desc 'Dump single table from production to dev'
      task :single_table, [:table_name] => :environment do |task, args|

        table_name = args.table_name

        unless File.exists?( "/tmp/production_#{table_name}.dump" )
          puts 'No local dump, retrieving ...'
          `ssh hw [ -e /tmp/production_#{table_name}.dump ]`
          unless $?.to_i == 0 # file exist
            # Dump and compress it
            puts 'No remote dump, pg_dump'
            `ssh hw pg_dump -Fc -n public -t #{table_name} -U eve_business_server eve_business_server_production -f /tmp/production_#{table_name}.dump`
          end
          # Get the remote file
          puts 'Retrieving remote dump'
          `scp hw:/tmp/production_#{table_name}.dump /tmp/`
        end

        # puts 'Dropping database'
        # `dropdb eve_business_server_dev -U eve_business_server`
        #
        # puts 'Creating database'
        # `createdb eve_business_server_dev -U eve_business_server -O eve_business_server`
        #
        `psql -U eve_business_server -d eve_business_server_dev -c "DROP TABLE #{table_name}"`

        puts 'Inserting datas'
        `pg_restore -U eve_business_server -d eve_business_server_dev -n public -t #{table_name} /tmp/production_#{table_name}.dump`
      end

    end
  end
end