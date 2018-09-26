class ItemsController < ApplicationController

  # before_action :require_logged_in!
  before_action :set_user

  caches_page :show

  include Modules::Nvl
  include Modules::CheckedProductionListIds

  def show
    @item = EveItem.find_by( id: params[ :id ] )
    @jita_min_price = PricesMin.find_by_eve_item_id_and_trade_hub_id( @item.id, get_jita.id )
    # redirect_to item_market_overview_path( @item )
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
