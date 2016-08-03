namespace :db do
  namespace :dump do
    namespace :prod_to_staging do

      desc 'Dump full database from prod to staging'
      task :full => :environment do

        `ssh hw [ -e /tmp/production_to_staging.sql ]`
        unless $?.to_i == 0 # file exist
          `ssh hw 'pg_dump -Ox -U eve_business_server -n production eve_business_server -f /tmp/production_to_staging.sql'`
        end

        puts 'Modifying prod dump'
        # `ssh hw "sed -i.bak 's/SET search_path = production, pg_catalog;/SET search_path = staging, pg_catalog;/' /tmp/production_to_staging.sql"`

        # `ssh hw 'rm tmp/production_to_staging.sql.bak'`

        puts 'Dropping database'
        `ssh hw "psql -U eve_business_server eve_business_server -c 'DROP SCHEMA staging'"`
        puts 'Creating database'
        `ssh hw 'psql -U eve_business_server -c \'CREATE SCHEMA staging\''`

        puts 'Creating database'
        `ssh hw 'psql -U eve_business_server eve_business_server < tmp/production_to_staging.sql'`

        `ssh hw 'rm tmp/production_to_staging.sql'`
      end

    end
  end
end
