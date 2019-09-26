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

		set_default_package( user )

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

	def set_default_package( user )
		return if user.initialization_finalized

		User.transaction do
			# User monitor Jita and Amarr
			[ 30000142, 30002187 ].each do |th_id|
				th = TradeHub.find_by_eve_system_id( th_id )
				user.trade_hubs << th unless user.trade_hubs.exists?( th.id )
			end

			[ 973, 972, 927, 917].each do |group|
				MarketGroup.find_by_cpp_market_group_id( group ).eve_items.each do |item|
					user.eve_items << item unless user.eve_items.exists?( item.id )
				end
			end

			user.initialization_finalized = true
			user.save!
		end

	end

end