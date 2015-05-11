require 'pp'

class SessionsController < ApplicationController

  def new
  end

  def create
    user = User.from_omniauth(env["omniauth.auth"])
    raise "User can't be found : #{user}" unless user
    session[:user_id] = user.id
    redirect_to root_url
  end

  def destroy
    session[:user_id] = nil
    redirect_to root_url
  end

  def failure
    redirect_to new_sessions_path, alert: "Authentication failed, please try again."
  end

end