require 'pp'

class ChooseItemsController < ApplicationController

  # autocomplete :eve_item, :name_lowcase, full: true

  before_action :require_logged_in!, :log_client_activity

  def edit
    @user = current_user
    @item_ids = @user.eve_item_ids.uniq
    @json_tree = File.open( 'data/items_tree.json' ).read
  end

  # TODO : add a limit in order to prevent to many items
  def select_items
    @user = current_user

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

  # def select_all_items
  #   @user = current_user
  #
  #   ActiveRecord::Base.transaction do
  #     @user.eve_items.clear
  #
  #     ActiveRecord::Base.connection.execute(
  #         "INSERT INTO eve_items_users (user_id, eve_item_id) SELECT #{current_user.id}, id FROM eve_items" )
  #
  #     @user.update_attribute(:last_changes_in_choices,Time.now)
  #   end
  #   redirect_to edit_choose_items_path
  # end

end
