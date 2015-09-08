require 'open-uri'
require 'open-uri/cached'
require 'pp'

OpenURI::Cache.cache_path = 'tmp'

class Crest::EveItemsFromCrest
  extend Crest::CrestBase

  def self.update_eve_items
    manage_cache

    ActiveRecord::Base.transaction do

      html_req = "https://public-crest.eveonline.com/market/types/"
      # puts html_req
      json_result = open( html_req ).read

      parsed_data = JSON.parse( json_result )

      parsed_data["items"].each do |item|
        market_group_id = item['marketGroup']['id']
        type_id = item['type']['id']
        name = item['type']['name']
        lcase_name = name.downcase
        eve_item = EveItem.find_by_cpp_eve_item_id( type_id )
        if eve_item
          eve_item.update_attribute( :cpp_market_group_id, market_group_id )
        else
          EveItem.create!( cpp_eve_item_id: type_id, name: name, name_lowcase: lcase_name, cpp_market_group_id: market_group_id )
        end
      end
    end
  end
end