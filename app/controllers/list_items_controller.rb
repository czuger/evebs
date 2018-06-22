class ListItemsController < ApplicationController

  before_action :require_logged_in!, :log_client_activity

  def edit
    @user = current_user
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
