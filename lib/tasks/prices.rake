require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'
EVE_CENTRAL_FILE_NAME='tmp/api.eve-central.com'

namespace :data_compute do

  desc "Feed min prices per trade hubs"
  task :trade_hubs_prices => :environment do
    # First compute used items and trade hubs
    puts 'About to recompute all min prices for selected items on all trade hubs'
    used_item, used_trade_hubs = User.get_used_items_and_trade_hubs
    used_trade_hubs.each do |trade_hub|
      puts "Retrieveing min prices for #{trade_hub.name}"
      used_item.each do |eve_item|
        puts "Retrieving min prices for #{eve_item.name}"
        eve_item.compute_min_price_for_system(trade_hub)
      end
    end
  end

  desc "Feed min prices per trade hubs for all items and all trade hubs"
  task :trade_hubs_prices_full => :environment do
    puts 'About to recompute all min prices for all items on all trade hubs'
    used_item, used_trade_hubs = User.get_used_items_and_trade_hubs
    TradeHub.all.each do |trade_hub|
      puts "Retrieveing min prices for #{trade_hub.name}"
      eve_item_ids = EveItem.all.map{ |ei| ei.cpp_eve_item_id }
      min_prices = MultiplePriceRetriever.get_prices( trade_hub.eve_system_id, eve_item_ids )
      min_prices.each_pair do |key,min_price|
        if min_price
          eve_item = EveItem.find_by_cpp_eve_item_id( key )
          min_price_item = MinPrice.find_by_eve_item_id_and_trade_hub_id( eve_item.id, trade_hub.id )
          unless min_price_item
            MinPrice.create!( eve_item: eve_item, trade_hub: trade_hub, min_price: min_price )
          else
            min_price_item.update_attribute( :min_price, min_price )
          end
        end
      end
    end
  end

  desc "Get best min marges"
  task :get_best_margin => :environment do
    puts 'Finding best margin'
    pp MinPrice.get_best_min_prices
  end

  desc "Compute min prices"
  task :compute_min_price_for_all_items => :environment do
    puts 'Computing min prices for all items'
    MinPrice.compute_min_price_for_all_items
  end

end