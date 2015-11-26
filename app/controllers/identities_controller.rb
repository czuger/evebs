class IdentitiesController < ApplicationController

  before_action :log_client_activity

  def new
    @identity = env['omniauth.identity']
  end

end
