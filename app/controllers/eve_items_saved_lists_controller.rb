class EveItemsSavedListsController < ApplicationController

  before_action :require_logged_in!

  def index
    @title = 'My items saved lists'
    @saved_lists = current_user.eve_items_saved_lists.paginate(:page => params[:page], :per_page => 20 )
  end

  def new
  end

  def create
    current_user_ids = current_user.eve_items_ids
    @saved_list = EveItemsSavedList.new( user: current_user, description: params[:description], saved_ids: current_user_ids )
    if @saved_list.save
      redirect_to eve_items_saved_lists_path, notice: 'List saved successfully'
    else
      render :saved_list
    end
  end

  def clear
    clear_user_list
    redirect_to eve_items_saved_lists_path, notice: 'List cleared successfully'
  end

  def destroy
    @saved_list = EveItemsSavedList.new( user: current_user, description: params[:description], saved_ids: current_user_ids )
    if @saved_list.save
      redirect_to eve_items_saved_lists_path, notice: 'List saved successfully'
    else
      render :saved_list
    end

  end

  def load
    saved_list = current_user.eve_items_saved_lists.find( params[:saved_list_id] )

    ActiveRecord::Base.transaction do
      clear_user_list

      saved_list&.saved_ids&.in_groups_of( 500 ).each do |g|
        links = []
        g.each do |eve_item_id|
          links << EveItemsUser.new( user_id: current_user.id, eve_item_id: eve_item_id, )
        end
        EveItemsUser.import( links )
      end
    end

    redirect_to saved_list_list_items_path, notice: 'List successfully restored'
  end

  private

  def clear_user_list
    EveItemsUser.where( user_id: @user ).delete_all
  end

end
