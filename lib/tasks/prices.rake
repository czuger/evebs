require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'
EVE_CENTRAL_FILE_NAME='tmp/api.eve-central.com'

namespace :data_compute do
  desc "Feed min prices per trade hubs"
  task :trade_hubs_prices => :environment do
    # First compute used items and trade hubs
    used_item = []
    used_trade_hubs = []
    User.all.to_a.each do |user|
      user.eve_items.each do |eve_item|
        used_item << eve_item unless used_item.include?( eve_item )
      end
      user.trade_hubs.each do |trade_hub|
        used_trade_hubs << trade_hub unless used_trade_hubs.include?( trade_hub )
      end
    end
     # Refresh the eve central API cache each half hour
    if File.exist?( EVE_CENTRAL_FILE_NAME ) && Time.now - File.ctime( EVE_CENTRAL_FILE_NAME ) > (3600/2)
      `rm -r tmp/api.eve-central.com`
    end
    used_trade_hubs.each do |trade_hub|
      used_item.each do |eve_item|
        html_req = "http://api.eve-central.com/api/quicklook?typeid=#{eve_item.cpp_eve_item_id}&usesystem=#{trade_hub.eve_system_id}"
        # pp html_req
        xml_result = open( html_req ).read
        dom = Nokogiri::XML( xml_result )
        price_page =  dom.xpath("//sell_orders//price")
        min = price_page.map{|e| e.children[0].to_s.to_i}.min
        min_price_item = MinPrice.where( 'eve_item_id = ? AND trade_hub_id = ?', eve_item.id, trade_hub.id ).first
        if min
          unless min_price_item
            new_min_price = MinPrice.new( eve_item: eve_item, trade_hub: trade_hub, min_price: min )
            new_min_price.save!
          else
            min_price_item.update_attribute( min_price: min )
          end
        else
          if min_price_item
            min_price_item.destroy
          end
        end
      end
    end
  end
end