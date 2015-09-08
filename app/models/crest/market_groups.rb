class Crest::MarketGroups

  extend Crest::CrestBase

  def self.update_market_group
    puts 'About to update market groups'
    manage_cache

    html_req = "https://public-crest.eveonline.com/market/types/"
    # puts html_req
    json_result = open( html_req ).read

    parsed_data = JSON.parse( json_result )

    parsed_data["items"].each do |item|
      market_group_id = item['marketGroup']['id']
      type_id = item['type']['id']
      eve_item = EveItem.find_by_cpp_eve_item_id(type_id)
      if eve_item
        eve_item.update_attribute( :cpp_market_group_id, market_group_id )
      end
    end
  end

end