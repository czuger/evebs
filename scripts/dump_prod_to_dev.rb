require 'optparse'
require 'ostruct'
require 'yaml'

LOCAL_DUMP_FILE = REMOTE_DUMP_FILE = '/tmp/production.dump'

options = {}
OptionParser.new do |opts|
  opts.banner = 'Usage: dump_prod_to_dev.rb [options]'

  opts.on('-l', 'Use local dumpfile') do |l|
    options[:use_local_dumpfile] = l
  end

  opts.on('-t', '--table TABLE_NAME', 'Import only table name') do |l|
    options[:import_table] = l
  end

  options = OpenStruct.new( options )

end.parse!

dev_db_data = OpenStruct.new( YAML.load_file( '../config/database.yml' )['development'] )

if options.import_table
  # Single table import

  table_name = options.import_table

  puts 'Dumping table on production server'
  `ssh pw pg_dump -Fc -n public -t #{table_name} -t #{table_name}_id_seq -U eve_business_server eve_business_server_production -f /tmp/production_#{table_name}.dump`

  puts 'Retrieving remote dump'
  `scp pw:/tmp/production_#{table_name}.dump /tmp/`

  puts "Dropping table #{table_name}"
  `psql #{dev_db_data.database} -h #{dev_db_data.host} -p #{dev_db_data.port} -c "DROP TABLE #{table_name};" -U #{dev_db_data.username}`

  puts 'Inserting datas'
  `pg_restore -O -d #{dev_db_data.database} -h #{dev_db_data.host} -p #{dev_db_data.port} -U #{dev_db_data.username} /tmp/production_#{table_name}.dump`

else
  # Full import

  raise 'Local dump file not found' if options.use_local_dumpfile && !File.exist?( LOCAL_DUMP_FILE )
  unless options.use_local_dumpfile
    puts 'Running pg_dump on remote environment.'
    `ssh pw pg_dump -Fc -n public -T "eve_market_history_archives" -U eve_business_server eve_business_server_production -f #{REMOTE_DUMP_FILE}`
    puts 'Retrieving remote dump'
    `scp pw:#{REMOTE_DUMP_FILE} /tmp/`
  end

  puts 'Dropping public schema'
# `dropdb eve_business_server_dev`
  `psql #{dev_db_data.database} -h #{dev_db_data.host} -p #{dev_db_data.port} -c "DROP SCHEMA public CASCADE;" -U #{dev_db_data.username}`

  puts 'Creating public schema'
# `createdb eve_business_server_dev`
  `psql #{dev_db_data.database} -h #{dev_db_data.host} -p #{dev_db_data.port} -c "CREATE SCHEMA public;" -U #{dev_db_data.username}`
  `psql #{dev_db_data.database} -h #{dev_db_data.host} -p #{dev_db_data.port} -c "GRANT ALL ON SCHEMA public TO dev;" -U #{dev_db_data.username}`

  puts 'Inserting datas'
  `pg_restore -O -d #{dev_db_data.database} -h #{dev_db_data.host} -p #{dev_db_data.port} -n public -U #{dev_db_data.username} #{LOCAL_DUMP_FILE}`
end

puts 'Data insert finished'