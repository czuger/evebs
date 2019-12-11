namespace :db do
  namespace :dump do
    namespace :production_to_dev do

      #  use task params :
      #
      # desc 'test'
      # task :test, [ :foo, :bar ]  => [:environment] do|task, args|
      #   p args.foo
      # end

      desc 'Dump full database from production to dev'
      task :full  => :environment do

        # p args, args.use_local_dump, (args.use_local_dump != 'y')

        use_local_pg_dump = false
        if File.exists?( '/tmp/production.dump' )
          # puts 'There already is a local dump. Do you want to remove it and refresh the dump ? (y/n)'
          # result = STDIN.gets.chomp
          use_local_pg_dump = (ENV['USE_LOCAL_PG_DUMP'] == 'y')
        end

        p ENV['USE_LOCAL_PG_DUMP']
        p use_local_pg_dump


        unless use_local_pg_dump
          puts 'No local dump, or local dump erased. Retrieving ...'
          `ssh nw [ -e /tmp/production.dump ]`

          use_remote_pg_dump = false
          if $?.to_i == 0
            # puts 'There already is a remote dump. Do you want to remove it and refresh the dump ? (y/n)'
            # result = STDIN.gets.chomp
            use_remote_pg_dump = (args.use_remote_dump == 'y')
          end

          unless use_remote_pg_dump # file exist
            # Dump and compress it
            puts 'Running pg_dump on remote environment.'
            `ssh nw pg_dump -Fc -n public -T "eve_market_history_archives" -U eve_business_server eve_business_server_production -f /tmp/production.dump`
          end
          # Get the remote file
          puts 'Retrieving remote dump'
          `scp nw:/tmp/production.dump /tmp/`
        end

        puts 'Dropping public schema'
        # `dropdb eve_business_server_dev`
        `psql dev -h localhost -p 5432 -c "DROP SCHEMA public CASCADE;" -U dev`

        puts 'Creating public schema'
        # `createdb eve_business_server_dev`
        `psql dev -h localhost -p 5432 -c "CREATE SCHEMA public;" -U dev`
        `psql dev -h localhost -p 5432 -c "GRANT ALL ON SCHEMA public TO dev;" -U dev`

        puts 'Inserting datas'
        `pg_restore -O -d dev -h localhost -p 5432 -n public -U dev /tmp/production.dump`
      end

    end
  end
end