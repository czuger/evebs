require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'
EVE_CENTRAL_FILE_NAME='tmp/api.eve-central.com'

namespace :data_compute do
  desc "Feed min prices per trade hubs"
  task :trade_hubs_prices => :environment do
    # First compute used items and trade hubs
    used_item, used_trade_hubs = User.get_used_items_and_trade_hubs
    used_trade_hubs.each do |trade_hub|
      puts "Retrieveing min prices for #{trade_hub.name}"
      used_item.each do |eve_item|
        puts "Retrieving min prices for #{eve_item.name}"
        eve_item.set_min_price(trade_hub)
      end
    end
  end
end