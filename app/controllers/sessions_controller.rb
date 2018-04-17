require 'pp'

class SessionsController < ApplicationController

  before_action :log_client_activity
  skip_before_action :verify_authenticity_token, only: :create, if: -> { Rails.env.development? }

  def new
  end

  def create
    user = User.from_omniauth(request.env['omniauth.auth'])
    raise "User can't be found : #{user}" unless user
    session[:user_id] = user.id
    redirect_to price_advices_advice_prices_url
  end

  def destroy
    session[:user_id] = nil
    redirect_to root_url
  end

  def failure
    redirect_to new_sessions_path, alert: "Authentication failed, please try again."
  end

end