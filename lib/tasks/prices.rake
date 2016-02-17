require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

namespace :data_compute do
  namespace :min_prices do
    desc "Retrieve min prices per trade hubs"
    task :used => :environment do
      # First compute used items and trade hubs
      puts '*'*100
      puts 'About to recompute all avg prices for selected items on all trade hubs'
      puts '*'*100
      used_items, used_trade_hubs = User.get_used_items_and_trade_hubs
      used_trade_hubs.each do |trade_hub|
        puts "Retrieveing min prices for #{trade_hub.name}"
        EveItem.compute_min_price_for_system( trade_hub, used_items )
      end
      puts '*'*100
      puts 'End of recomputing all avg prices for selected items on all trade hubs'
      puts '*'*100
      puts
    end

    desc "Retrieve min prices of all items for jita"
    task :jita => :environment do
      # First compute used items and trade hubs
      puts '*'*100
      puts 'About to recompute all avg prices for all items on jita'
      puts '*'*100
      used_items = EveItem.all
      used_trade_hubs = [ TradeHub.find_by_eve_system_id( Component::JITA_EVE_SYSTEM_ID ) ]
      used_trade_hubs.each do |trade_hub|
        puts "Retrieveing min prices for #{trade_hub.name}"
        EveItem.compute_min_price_for_system( trade_hub, used_items )
      end
      puts '*'*100
      puts 'End of recomputing all avg prices for all items for Jita'
      puts '*'*100
      puts
    end

    desc "Feed min prices per trade hubs for all items and all trade hubs"
    task :all => :environment do
      puts '*'*100
      puts 'About to recompute all min prices for all items on all trade hubs'
      puts '*'*100
      used_item, used_trade_hubs = User.get_used_items_and_trade_hubs
      TradeHub.all.each do |trade_hub|
        puts "Retrieveing min prices for #{trade_hub.name}"
        eve_items = EveItem.all
        puts "Retrieveing min prices for #{trade_hub.name}"
        EveItem.compute_min_price_for_system( trade_hub, eve_items )
      end
      puts '*'*100
      puts 'End of recomputing all min prices for all items on all trade hubs'
      puts '*'*100
      puts
    end

  end

end