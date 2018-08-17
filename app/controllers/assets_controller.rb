class AssetsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  def show
    @assets = @user.bpc_assets.includes( :station_detail, :blueprint_component )
  end

end
