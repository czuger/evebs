class ItemsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  include Modules::Nvl

  def index
    @user = current_user
    @item_ids = @user.eve_item_ids.uniq
  end

  def cost
    @item = EveItem.includes( :blueprint ).find_by( id: params[ :item_id ] )
  end

  def show
    @item = EveItem.find( params[ :id ] )

    if @item.prices_advices.exists?
      @item_prices = @item.prices_advices.includes( { trade_hub: :region } ).order( 'vol_month DESC NULLS LAST' )
    else
      @min_prices = @item.prices_mins.includes( { trade_hub: :region } ).order( 'min_price ASC NULLS LAST' )
    end
  end

end
