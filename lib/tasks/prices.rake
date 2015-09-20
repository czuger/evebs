require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

namespace :data_compute do
  namespace :min_prices do
    desc "Retrieve min prices per trade hubs"
    task :used => :environment do
      # First compute used items and trade hubs
      puts 'About to recompute all avg prices for selected items on all trade hubs'
      used_items, used_trade_hubs = User.get_used_items_and_trade_hubs
      used_trade_hubs.each do |trade_hub|
        puts "Retrieveing min prices for #{trade_hub.name}"
        EveItem.compute_min_price_for_system( trade_hub, used_items )
      end
    end

    desc "Feed min prices per trade hubs for all items and all trade hubs"
    task :all => :environment do
      puts 'About to recompute all min prices for all items on all trade hubs'
      used_item, used_trade_hubs = User.get_used_items_and_trade_hubs
      TradeHub.all.each do |trade_hub|
        puts "Retrieveing min prices for #{trade_hub.name}"
        eve_items = EveItem.all
        puts "Retrieveing min prices for #{trade_hub.name}"
        EveItem.compute_min_price_for_system( trade_hub, eve_items )
      end
    end

  end

end