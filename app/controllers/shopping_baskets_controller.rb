class ShoppingBasketsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def show
    @user = current_user
    @basket_active_record = @user.shopping_baskets.joins( :trade_hub, :eve_item, { trade_hub: :region } ).
        joins( 'LEFT JOIN prices_advices ON prices_advices.eve_item_id = shopping_baskets.eve_item_id AND prices_advices.trade_hub_id = shopping_baskets.trade_hub_id' )
                                .order( 'trade_hubs.name', 'eve_items.name' ).paginate( :page => params[:page], :per_page => 20 )

    @basket_array = @basket_active_record.pluck_to_hash( 'trade_hubs.name', 'regions.name', 'eve_items.name', 'eve_items.id',
                                                         :vol_month, :min_price, :single_unit_cost, 'trade_hubs.id' )
  end

end
