require 'open-uri'
require 'open-uri/cached'
require 'pp'

class Crest::ItemPrices
  extend Crest::CrestBase

  manage_cache

  def self.get(market_id,item_id)

    html_req = "https://public-crest.eveonline.com/market/#{market_id}/types/#{item_id}/history/"
    # puts html_req
    json_result = open( html_req ).read

    parsed_data = JSON.parse( json_result )

    parsed_data["items"].each do |item|
      puts item.inspect
    end
  end
end