class ListItemsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

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

  private

  def items_list( my_items_only )
    @user = current_user
    @item_ids = @user.eve_item_ids.uniq.to_set

    if my_items_only
      @items = @user.eve_items
    else
      @items = EveItem.all
    end

    if params['filter']
      @items = @items.where( "lower( name ) like '%#{params['filter']}%'" ).order( 'name' )
    else
      @items = EveItem.none unless my_items_only
    end

    # p @items.to_sql

    @items = @items.paginate(:page => params[:page], :per_page => 20 )
    @filter = params['filter']
  end
end
