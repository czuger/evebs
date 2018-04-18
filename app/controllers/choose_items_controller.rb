require 'pp'

class ChooseItemsController < ApplicationController

  # autocomplete :eve_item, :name_lowcase, full: true

  before_action :require_logged_in!, :log_client_activity

  def edit
    @user = current_user
    @item_ids = @user.eve_item_ids.uniq
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

end
