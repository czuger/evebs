namespace :db do
  namespace :dump do
    namespace :prod_to_dev do

      desc 'Dump all database from prod to dev'
      task :full => :environment do

        unless File.exists?( 'tmp/production.sql' )
          `ssh hw [ -e /tmp/production.sql.gz ]`
          unless $?.to_i == 0 # file exist
            # Dump and compress it
          end
          # Get the remote file
          puts 'Retrieving prod dump'
          `scp hw:/tmp/production.sql.gz tmp/`
          puts 'Unzipping prod dump'
          `gunzip tmp/production.sql.gz`
        end

        puts 'Modifying prod dump'
        `sed -i.bak '/SET search_path = production, pg_catalog;/d' tmp/production.sql`
        `sed -i.bak '/CREATE SCHEMA production;/d' tmp/production.sql`
        `sed -i.bak '/ALTER SCHEMA production OWNER TO eve_business_server;/d' tmp/production.sql`

        File.unlink( 'tmp/production.sql.bak' )

        puts 'Dropping database'
        `psql -U eve_business_server -c 'DROP DATABASE eve_business_server_dev'`
        puts 'Creating database'
        `psql -U eve_business_server -c 'CREATE DATABASE eve_business_server_dev'`

        puts 'Creating database'
        `psql -U eve_business_server eve_business_server_dev < tmp/production.sql`
      end

      desc "Dump user table from prod to dev"
      task :users => :environment do

        `ssh hw 'pg_dump --column-inserts --data-only -U eve_business_server -t production.users > /tmp/users.sql'`
        `scp hw:/tmp/users.sql /tmp/`
        `ssh hw 'rm /tmp/users.sql'`
        `sed -i.bak '/SET search_path = production, pg_catalog;/d' /tmp/users.sql`
        `psql -U eve_business_server eve_business_server_dev < /tmp/users.sql`

      end
    end
  end
end
