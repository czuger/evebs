require 'pp'

class SessionsController < ApplicationController

  before_action :log_client_activity
  # There is a strange behavior : if and only can't be used together
  # see : https://github.com/rails/rails/issues/9703
  # But skipping authenticity token for all actions in dev is fine.
  skip_before_action :verify_authenticity_token, if: -> { Rails.env.test? }


  def create
    user = User.from_omniauth(request.env['omniauth.auth'])
    raise "User can't be found : #{user}" unless user
    session[:user_id] = user.id
    redirect_to buy_orders_path
  end

  def destroy
    session[:user_id] = nil
    redirect_to root_url
  end

  def failure
    redirect_to new_sessions_path, alert: "Authentication failed, please try again."
  end

end