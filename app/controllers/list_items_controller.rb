class ListItemsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def edit
    @user = current_user
    @items = EveItem.where( "name_lowcase like '%#{params['filter']}%'" ).order( 'name' ).paginate(:page => params[:page], :per_page => 15)
    @filter = params['filter']
    @item_ids = @user.eve_item_ids.uniq.to_set
  end

  def update
    @user = current_user

    current_ids = @user.eve_item_ids
    to_remove_ids = params['items'].keys.map(&:to_i)
    current_ids -= to_remove_ids

    @user.eve_item_ids = current_ids
    redirect_to edit_list_items_path
  end
end
