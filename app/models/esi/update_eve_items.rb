class Esi::UpdateEveItems < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update

    Banner.p 'About to remove unused eve items'

    EveItem.where.not( cpp_eve_item_id: Blueprint.select( :produced_cpp_type_id ) ).destroy_all

    Banner.p 'About to update new eve items list.'

    blueprint_without_corresponding_items = Blueprint.where.not( produced_cpp_type_id: EveItem.select( :cpp_eve_item_id ) )

    Banner.p "About to download #{blueprint_without_corresponding_items.count} items."
    updated_items = downloaded_items = 0

    market_transformation_hash = Hash[ MarketGroup.pluck( :cpp_market_group_id, :id ) ]

    ActiveRecord::Base.transaction do
      blueprint_without_corresponding_items.each do |bp|
        @rest_url = "universe/types/#{bp.produced_cpp_type_id}/"
        cpp_item = get_page_retry_on_error

        downloaded_items += 1

        if downloaded_items % 10 == 0
          puts "Downloaded items : #{downloaded_items} / #{blueprint_without_corresponding_items.count}." if @debug_request
        end

        next unless cpp_item['published']

        item = EveItem.where( cpp_eve_item_id: bp.produced_cpp_type_id ).first_or_initialize

        item.name = cpp_item['name']
        item.market_group_id = market_transformation_hash[ cpp_item['market_group_id'] ]
        item.blueprint_id = bp.id
        item.save!

        updated_items += 1
      end
    end

    puts "Items downloaded : #{blueprint_without_corresponding_items.count}, items updated : #{updated_items}."
  end
end