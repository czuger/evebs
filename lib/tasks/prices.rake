require 'open-uri'
# require 'open-uri/cached'
require 'pp'

# OpenURI::Cache.cache_path = 'tmp'

namespace :data_compute do

  desc 'Download min prices'
  task :min_prices => :environment do
    Banner.p 'About to download min prices.'
    Esi::MinPrices.new(debug_request: false ).update
  end

  desc 'Compute prices advices'
  task :prices_advices => :environment do
    puts 'About to recompute prices advices.'
    PricesAdvice.update
  end

  # TODO : to remove
  # namespace :min_prices do
  #
  #   desc "Retrieve min prices per trade hubs"
  #   task :used => :environment do
  #     # First compute used items and trade hubs
  #     random_hex = SecureRandom.hex
  #     puts '*'*120
  #     puts "About to recompute all avg prices for selected items on all trade hubs : #{random_hex}"
  #     puts '*'*120
  #     retrieve_start = Time.now
  #     used_items, used_trade_hubs = User.get_used_items_and_trade_hubs
  #     updated_items_count = 0
  #     used_trade_hubs.each do |trade_hub|
  #       puts "Retrieveing min prices for #{trade_hub.name}"
  #       updated_items_count += EveItem.compute_min_price_for_system( trade_hub, used_items )
  #     end
  #     retrieve_end = Time.now
  #     MinPricesLog.create!( retrieve_start: retrieve_start, retrieve_end: retrieve_end,
  #                           duration: retrieve_end - retrieve_start, updated_items_count: updated_items_count,
  #                           random_hash: random_hex )
  #     puts '*'*120
  #     puts "End of recomputing all avg prices for selected items on all trade hubs : #{random_hex}"
  #     puts '*'*120
  #     puts
  #   end
  #
  #   desc "Retrieve min prices of all items for jita"
  #   task :jita => :environment do
  #     # First compute used items and trade hubs
  #     puts '*'*120
  #     puts 'About to recompute all avg prices for all items on jita'
  #     puts '*'*120
  #     used_items = EveItem.all
  #     used_trade_hubs = [ TradeHub.find_by_eve_system_id( Component::JITA_EVE_SYSTEM_ID ) ]
  #     used_trade_hubs.each do |trade_hub|
  #       puts "Retrieveing min prices for #{trade_hub.name}"
  #       EveItem.compute_min_price_for_system( trade_hub, used_items )
  #     end
  #     puts '*'*120
  #     puts 'End of recomputing all avg prices for all items for Jita'
  #     puts '*'*120
  #     puts
  #   end
  #
  #   desc "Feed min prices per trade hubs for all items and all trade hubs"
  #   task :all => :environment do
  #     puts '*'*120
  #     puts 'About to recompute all min prices for all items on all trade hubs'
  #     puts '*'*120
  #     used_item, used_trade_hubs = User.get_used_items_and_trade_hubs
  #     TradeHub.all.each do |trade_hub|
  #       puts "Retrieveing min prices for #{trade_hub.name}"
  #       eve_items = EveItem.all
  #       puts "Retrieveing min prices for #{trade_hub.name}"
  #       EveItem.compute_min_price_for_system( trade_hub, eve_items )
  #     end
  #     puts '*'*120
  #     puts 'End of recomputing all min prices for all items on all trade hubs'
  #     puts '*'*120
  #     puts
  #   end

  # end

end