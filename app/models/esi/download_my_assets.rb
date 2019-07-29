require_relative 'download'

class Esi::DownloadMyAssets < Esi::Download

  def initialize( debug_request: false )
    super( nil, {}, debug_request: debug_request )

    # $stdout = File.new('log/download_assets.log', 'w')
    # $stderr = File.new('log/download_assets.err', 'w')
    # $stdout.sync = true
    # $stderr.sync = true

    # p 'Thread started'
  end

  def update( user )
    Misc::Banner.p 'About to download users assets' if @verbose_output

    ActiveRecord::Base.transaction do

      user.bpc_assets.update_all( touched: false )
      user.bpc_assets_stations.update_all( touched: false )

      download_assets user

      user.bpc_assets.where( touched: false ).delete_all
      user.bpc_assets_stations.where( touched: false ).delete_all

      user.update( download_assets_running: false, last_assets_download: Time.now )
    end

  end

  private

  def download_assets( user )
    if user.locked && user.id != 3
      puts "#{user.name} is locked. Skipping ..."
      return
    end

    user_id = user.uid
    @rest_url = "characters/#{user_id}/assets/"

    return unless set_auth_token( user )

    p @rest_url if @verbose_output

    pages = get_all_pages
    p 'Pages retrieved' if @verbose_output

    unless pages
      user.update( locked: true )
      return
    end

    ActiveRecord::Base.transaction do
      pages.each do |asset|
        p asset if @verbose_output
        eve_item_id = EveItem.find_by_cpp_eve_item_id(asset['type_id'])&.id
        next unless eve_item_id

        trade_hub_id = UniverseStation.find_by_cpp_station_id(asset['location_id'])&.id

        to = BpcAsset.where( user_id: user.id, eve_item_id: eve_item_id, universe_station_id: trade_hub_id ).first_or_initialize
        to.quantity = asset['quantity']
        to.touched = true
        to.save!

        if trade_hub_id
          bas = BpcAssetsStation.where( user_id: user.id, universe_station_id: trade_hub_id ).first_or_initialize
          bas.touched = true
          bas.save!
        end

      end
    end
  end

end