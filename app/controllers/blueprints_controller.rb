class BlueprintsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user, only: [:show]

  def show
    @blueprint_modifications = @user.blueprint_modifications.joins( :blueprint ).order( 'blueprints.name' ).includes( :blueprint )
  end

end
