class AssetsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    @assets = @user.bpc_assets.includes( :station_detail, :blueprint_component )
    @stations_select_data = @assets.map{ |e| [ e.station_detail&.name, e.station_detail_id ] if e.station_detail_id }.uniq.compact.sort
  end

end
