require 'open-uri'
require 'open-uri/cached'
require 'pp'

class Crest::GetPriceHistory
  include Crest::CrestBase

  def initialize( low_level_transactions = false )
    get_watched_items_and_region_only(low_level_transactions)

    # Update monthly averages
    Crest::ComputePriceHistoryAvg.new
  end

  def get_watched_items_and_region_only(low_level_transactions)
    used_items, used_trade_hubs = User.get_used_items_and_trade_hubs
    regions = used_trade_hubs.map{ |e| e.region }
    used_items = used_items.map{ |e| [e.id,e.cpp_eve_item_id] }
    regions.each do |region|
      puts "About to retrieve price history for #{region.name}"
      if low_level_transactions
        get_region_history( region, used_items )
      else
        ActiveRecord::Base.transaction{get_region_history( region, used_items )}
      end
    end
  end

  def full_get(low_level_transactions)
    eve_item_ids_involved_in_blueprints = EveItem.where( involved_in_blueprint: true ).pluck( :id, :cpp_eve_item_id )
    Region.all.each do |region|
      puts "About to retrieve price history for #{region.name}"
      if low_level_transactions
        get_region_history( region, eve_item_ids_involved_in_blueprints )
      else
        ActiveRecord::Base.transaction{get_region_history( region, eve_item_ids_involved_in_blueprints )}
      end
    end
  end

  private

  def get_region_history( region, eve_item_ids_involved_in_blueprints )
    eve_item_ids_involved_in_blueprints.each do |eve_item_array|
      begin
        get( region, eve_item_array )
      rescue OpenURI::HTTPError
        # Nevermind if we can't read
      rescue StandardError => e
        p e.inspect
        p e.message
        p e.backtrace
        exit
      end
    end
  end

  def get( region, eve_item_array )

    html_req = get_crest_url( "market/#{region.cpp_region_id}/types/#{eve_item_array[1]}/history" )
    # puts html_req
    json_result = open( html_req ).read

    parsed_data = JSON.parse( json_result )

    items = parsed_data['items']
    present_timestamps = CrestPriceHistory.where( region_id: region.id, eve_item_id: eve_item_array[0] ).pluck( :day_timestamp )
    inserts = 0

    ActiveRecord::Base.transaction do

      items.each do |item_data|

        date_info = DateTime.parse( item_data['date'] )
        date_info_ts = date_info.strftime( '%Y%m%d' )
        # If we already have an information for that day, we process next record.
        next if present_timestamps.include?( date_info_ts )

        # puts "About to insert #{item_data.inspect}"
        CrestPriceHistory.create!( region_id: region.id, eve_item_id: eve_item_array[0], day_timestamp: date_info_ts, history_date: date_info,
        order_count: item_data['orderCount'], volume: item_data['volume'],
        low_price: item_data['lowPrice'], avg_price: item_data['avgPrice'], high_price: item_data['highPrice'] )

        inserts += 1
      end

    end

    puts "#{inserts} inserts for type #{eve_item_array[1]}"
  end
end