class MyAssetsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    set_small_screen
    @title = 'My assets'

    @selected_station_id = @user.selected_assets_station_id
    @stations_select_data = @user.bpc_assets_stations_details.map{ |e| [ e.name, e.id ] }.sort

    lad = @user.last_assets_download ? @user.last_assets_download : Time.at( 0 )
    @data_available_in = (lad + BpcAsset::CACHE_DURATION - Time.now).round

    @assets = @selected_station_id ? @user.bpc_assets.where( universe_station_id: @selected_station_id ).includes( :universe_station, :eve_item ).order( 'quantity DESC' ) : []
  end

  def update
    @user.update( download_assets_running: true )
    DownloadMyAssetsJob.perform_later( @user )
    redirect_to my_assets_path
  end

  def set_assets_station
    @user.update( selected_assets_station_id: params[:asset_station_id] )
    redirect_to my_assets_path
  end

end
