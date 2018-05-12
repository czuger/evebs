class Esi::EveItems < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update
    new_ids = TypeInRegion.distinct.pluck( :cpp_type_id )
    market_transformation_hash = Hash[ MarketGroup.pluck( :cpp_market_group_id, :id ) ]

    new_ids.each do |missing_id|
      @rest_url = "universe/types/#{missing_id}/"
      cpp_item = get_page_retry_on_error

      next unless cpp_item['published']

      item = EveItem.where( cpp_eve_item_id: missing_id ).first_or_initialize do |i|
        i.name = cpp_item['name']
        i.name_lowcase = i.name.downcase
        i.market_group_id = market_transformation_hash[ cpp_item['market_group_id'] ]
      end
      item.save!
    end

    puts "Items updated : #{new_ids.count}"

  end
end