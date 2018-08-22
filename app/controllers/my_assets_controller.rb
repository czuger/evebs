class MyAssetsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    @assets = @user.bpc_assets.includes( :station_detail, :blueprint_component )
    @stations_select_data = @user.bpc_assets_stations_details.map{ |e| [ e.name, e.id ] }.sort
  end

  def update
    @user.update( download_assets_running: true )
    DownloadMyAssetsJob.perform_later( @user )
    redirect_to my_assets_path
  end

end
