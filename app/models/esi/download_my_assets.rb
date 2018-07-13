require_relative 'download'

class Esi::DownloadMyAssets < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )
  end

  def update
    Banner.p 'About to download users assets'

    ActiveRecord::Base.transaction do

      BpcAsset.update_all( touched: false )

      Character.all.each do |character|
        puts "About to download #{character.name}"
        download_assets character
      end

      BpcAsset.where( touched: false ).delete_all
    end

  end

  private

  def download_assets( character )
    if character.locked && character.id != 3
      puts "#{character.name} is locked. Skipping ..."
      return
    end

    character_id = character.eve_id
    @rest_url = "characters/#{character_id}/assets/"

    set_auth_token( character )

    pages = get_all_pages

    unless pages
      character.update( locked: true )
      return
    end

    ActiveRecord::Base.transaction do
      pages.each do |asset|
        eve_item_id = BlueprintComponent.find_by_cpp_eve_item_id(asset['type_id'])&.id
        next unless eve_item_id

        trade_hub_id =  StationDetail.find_by_cpp_station_id(asset['location_id'])&.id

        to = BpcAsset.where( character_id: character.id, blueprint_component_id: eve_item_id, station_detail_id: trade_hub_id ).first_or_initialize
        to.quantity = asset['quantity']
        to.touched = true
        to.save!
      end
    end
  end

end