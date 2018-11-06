class ListItemsController < ApplicationController

  before_action :require_logged_in!, except: [ :edit ]
  before_action :set_user

  include Modules::CheckedProductionListIds

  def edit
    items_list false
  end

  def my_items_list
    items_list true
  end

  def update
    @user = current_user

    current_ids = @user.eve_item_ids
    to_remove_ids = params['items'].keys.map(&:to_i)
    current_ids -= to_remove_ids

    @user.eve_item_ids = current_ids
    redirect_to edit_list_items_path
  end

  def selection_change
    item = EveItem.find( params['id'] )

    if params['check_state'] == 'false'
      @user.eve_items.delete( item )
    else
      unless @user.eve_items.exists?( item.id )
        @user.eve_items << item
      end
    end
  end

  def clear
    @user.eve_items.clear
    redirect_to my_items_list_list_items_path
  end

  def save
    @saved_list = SavedList.new( user: @user, description: params[:description], saved_ids: @user.eve_item_ids )
    if @saved_list.save
      redirect_to saved_list_list_items_path, notice: 'List saved successfully'
    else
      render :saved_list
    end
  end

  def restore
    saved_list = @user.eve_items_saved_lists.find( params[:saved_list_id] )
    saved_list_ids = saved_list&.saved_eve_items_ids || []
    @user.eve_items_saved_lists = saved_list_ids
    redirect_to saved_list_list_items_path
  end

  def saved_list
    @saved_lists = @user.eve_items_saved_lists
  end

  private

  def items_list( my_items_only )
    @user = current_user
    @jita = TradeHub.find_by_eve_system_id( 30000142 )

    if @user
      @item_ids = @user.eve_item_ids.uniq.to_set
      set_checked_production_list_ids
    end

    if my_items_only
      @items = @user.eve_items
    else
      @items = EveItem.all
    end

    if params['filter']
      @items = @items.where( "lower( name ) like '%#{params['filter'].downcase}%'" )
    else
      @items = EveItem.none unless my_items_only
    end

    @items = @items.order( 'market_group_id, name' )

    # p @items.to_sql

    @items = @items.paginate(:page => params[:page], :per_page => 20 )
    @filter = params['filter']
  end
end
