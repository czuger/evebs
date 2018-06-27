class Esi::DownloadEveItems < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
    # p @errors_limit_remain
  end

  def update

    Banner.p 'About to remove unused eve items'

    EveItem.where.not( cpp_eve_item_id: Blueprint.select( :produced_cpp_type_id ) ).destroy_all

    Banner.p 'About to update new eve items list.'

    new_ids = Blueprint.where.not( produced_cpp_type_id: EveItem.select( :cpp_eve_item_id ) ).pluck( :produced_cpp_type_id )

    Banner.p "About to download #{new_ids.count} items."
    updated_items = downloaded_items = 0

    ActiveRecord::Base.transaction do
      new_ids.each do |missing_blueprint_id|
        @rest_url = "universe/types/#{missing_blueprint_id}/"
        cpp_item = get_page_retry_on_error

        downloaded_items += 1

        if downloaded_items % 1000 == 0
          puts "Downloaded items : #{downloaded_items} / #{new_ids.count}." if @debug_request
        end

        next unless cpp_item['published']

        item = EveItem.where( cpp_eve_item_id: missing_blueprint_id ).first_or_initialize

        item.name = cpp_item['name']
        item.name_lowcase = item.name.downcase
        item.market_group_id = market_transformation_hash[ cpp_item['market_group_id'] ]
        item.blueprint_id = missing_blueprint_id
        item.save!

        updated_items += 1
      end
    end

    puts "Items downloaded : #{new_ids.count}, items updated : #{updated_items}."
  end
end