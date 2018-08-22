class MyAssetsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    @selected_station_id = @user.selected_assets_station_id
    @stations_select_data = @user.bpc_assets_stations_details.map{ |e| [ e.name, e.id ] }.sort
    @data_available_in = (@user.last_assets_download + BpcAsset::CACHE_DURATION - Time.now).round
    @assets = @selected_station_id ? @user.bpc_assets.where( station_detail_id: @selected_station_id ).includes( :station_detail, :blueprint_component ) : []
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
