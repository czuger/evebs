namespace :dump_prod_to_dev do

  desc "Dump user table from prod to dev"
  task :users => :environment do

    `ssh hw 'pg_dump --column-inserts --data-only -U eve_business_server -t production.users > /tmp/users.sql'`
    `scp hw:/tmp/users.sql /tmp/`
    `ssh hw 'rm /tmp/users.sql'`
    `sed -i.bak '/SET search_path = production, pg_catalog;/d' /tmp/users.sql`
    `psql -U eve_business_server eve_business_server_dev < /tmp/users.sql`

  end

end
