class ItemsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity
  before_action :set_user

  include Modules::Nvl
  include Modules::CheckedProductionListIds

  def cost
    @item = EveItem.find_by( id: params[ :item_id ] )

    if @item.base_item
      jita = TradeHub.find_by_eve_system_id( 30000142 )
      @sales_final_detail = SalesFinal.where( eve_item_id: @item.id, trade_hub_id: jita.id ).
          where( 'volume > 0 AND day >= ( current_date - 7 )' ).order( 'day DESC, created_at DESC' ).
          paginate( :page => params[:page] )
    end
  end

  def show
    @item = EveItem.find( params[ :id ] )

    # set_checked_production_list_ids

    if @item.base_item
      @item_prices = @item.prices_mins.includes( {trade_hub: :region} ).order( 'min_price NULLS LAST' )
    else
      @item_prices = @item.price_advices_min_prices.order( 'vol_month DESC NULLS LAST, margin_percent DESC NULLS LAST' )
    end

  end

  def trade_hub_detail
    @trade_hub = TradeHub.find( params[ :trade_hub_id ] )
    @element = EveItem.find( params[ :item_id ] )
    @orders = PublicTradeOrder.where( trade_hub_id: params[ :trade_hub_id ], eve_item_id: params[ :item_id ], is_buy_order: false )
                  .order( 'price' ).limit( 20 )
  end

  # This part is for treeview only

  def items_tree
    @item_ids = @user.eve_item_ids.uniq
    @json_tree = File.open( 'data/items_tree.json' ).read
  end

  def items_tree_select
    if params[ :item ] == 'true'
      ActiveRecord::Base.transaction do
        item = EveItem.find( params[ :id ] )
        if params[ :check_state ] == 'true'
          @user.eve_items << item unless @user.eve_items.exists?( id: item.id )
        else
          @user.eve_items.delete( item )
        end
        @user.update_attribute(:last_changes_in_choices,Time.now)
      end
    end
    head :ok
  end

end
