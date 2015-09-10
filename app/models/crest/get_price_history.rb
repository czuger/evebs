require 'open-uri'
require 'open-uri/cached'
require 'pp'

class Crest::GetPriceHistory
  include Crest::CrestBase


  def get_region_history( region )
    # ActiveRecord::Base.transaction do
      EveItem.where( involved_in_blueprint: true ).find_each do |eve_item|
        begin
          get( region, eve_item )
        rescue OpenURI::HTTPError
          # Nevermind if we can't read
        rescue StandardError => e
          p e.inspect
          p e.message
          p e.backtrace
          exit
        end
      end
    # end
  end

  private

  def get( region, eve_item )

    manage_cache

    html_req = get_crest_url( "market/#{region.cpp_region_id}/types/#{eve_item.cpp_eve_item_id}/history" )
    puts html_req
    json_result = open( html_req ).read

    parsed_data = JSON.parse( json_result )

    ActiveRecord::Base.transaction do

      parsed_data["items"].each do |item_data|
        date_info = DateTime.parse( item_data['date'] )
        date_info_ts = date_info.strftime( '%Y%m%d' )
        history = CrestPriceHistory.where( region_id: region.id, eve_item_id: eve_item.id, day_timestamp: date_info_ts ).first
        unless history
          CrestPriceHistory.create!( region_id: region.id, eve_item_id: eve_item.id, day_timestamp: date_info_ts, history_date: date_info,
          order_count: item_data['orderCount'], volume: item_data['volume'],
          low_price: item_data['lowPrice'], avg_price: item_data['avgPrice'], high_price: item_data['highPrice'] )
        end
      end

    end
  end
end