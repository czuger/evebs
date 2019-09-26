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

		default_package( user )

    redirect_to buy_orders_path
  end

  def destroy
    session[:user_id] = nil
    redirect_to root_url
  end

  def failure
    redirect_to new_sessions_path, alert: "Authentication failed, please try again."
  end

	private

	def default_package( user )
		# User monitor Jita
		user.trade_hubs << TradeHub.find_by_eve_system_id( 30000142 )
		user.trade_hubs << TradeHub.find_by_eve_system_id( 30002187 )

		[ 973, 972, 927, 917].each do |group|
			MarketGroup.find_by_cpp_market_group_id( group ).eve_items.each do |item|
				user.eve_items << item
			end

		end

	end

end