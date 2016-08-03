namespace :db do
  namespace :dump do
    namespace :staging_to_dev do

      desc 'Dump full database from staging to dev'
      task :full => :environment do

        unless File.exists?( '/tmp/staging.dump' )
          puts 'No local dump, retrieving ...'
          `ssh hw [ -e /tmp/staging.dump ]`
          unless $?.to_i == 0 # file exist
            # Dump and compress it
            puts 'No remote dump, pg_dump'
            # TODO : faire un test avec uniquement le schema public.
            `ssh hw pg_dump -Fc -n public -U eve_business_server eve_business_server_staging -f /tmp/staging.dump`
          end
          # Get the remote file
          puts 'Retrieving remote dump'
          `scp hw:/tmp/staging.dump /tmp/`
        end

        puts 'Dropping database'
        `dropdb eve_business_server_dev -U postgres`

        puts 'Creating database'
        `createdb eve_business_server_dev -U postgres -O eve_business_server`

        puts 'Inserting datas'
        `pg_restore -U eve_business_server -d eve_business_server_dev -n public < /tmp/staging.dump`
      end

    end
  end
end
