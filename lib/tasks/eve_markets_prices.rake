require 'yaml'

namespace :data_download do

  desc 'Download eve markets/prices'
  task :eve_markets_prices => :environment do
    puts 'About to fill the table eve_markets_prices'
    Esi::DownloadMarketsPrices.new( debug_request: true ).fill_table
  end


end