class BlueprintsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [:show]

  def show
    @blueprint_modifications = @user.blueprint_modifications.joins( :blueprint ).order( 'blueprints.name' )
                                   .includes( :blueprint ).paginate(:page => params[:page], :per_page => 20 )

    lbd = @user.last_blueprints_download ? @user.last_blueprints_download : Time.at( 0 )
    @data_available_in = (lbd + BpcAsset::CACHE_DURATION - Time.now).round
  end

end
