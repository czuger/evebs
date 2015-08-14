require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'
EVE_CENTRAL_FILE_NAME='tmp/api.eve-central.com'

namespace :data_compute do

  desc "Retrieve min prices per trade hubs"
  task :trade_hubs_prices => :environment do
    # First compute used items and trade hubs
    puts 'About to recompute all avg prices for selected items on all trade hubs'
    used_items, used_trade_hubs = User.get_used_items_and_trade_hubs
    used_trade_hubs.each do |trade_hub|
      puts "Retrieveing min prices for #{trade_hub.name}"
      EveItem.compute_min_price_for_system( trade_hub, used_items )
    end
  end

  desc "Feed min prices per trade hubs for all items and all trade hubs"
  task :trade_hubs_prices_full => :environment do
    puts 'About to recompute all min prices for all items on all trade hubs'
    used_item, used_trade_hubs = User.get_used_items_and_trade_hubs
    TradeHub.all.each do |trade_hub|
      puts "Retrieveing min prices for #{trade_hub.name}"
      eve_items = EveItem.all
      puts "Retrieveing min prices for #{trade_hub.name}"
      EveItem.compute_min_price_for_system( trade_hub, eve_items )
    end
  end

  # desc "Get best min marges"
  # task :get_best_margin => :environment do
  #   puts 'Finding best margin'
  #   pp MinPrice.get_best_min_prices
  # end
  #
  # desc "Compute min prices"
  # task :compute_min_price_for_all_items => :environment do
  #   puts 'Computing min prices for all items'
  #   MinPrice.compute_min_price_for_all_items
  # end

end