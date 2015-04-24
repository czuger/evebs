require 'pp'

class ChooseItemsController < ApplicationController

  # autocomplete :eve_item, :name_lowcase, full: true

  before_action :require_logged_in!

  def edit
    if current_user
      @user = current_user
      @items = @user.eve_items.order(:name)
      @per_group_count = (@items.length/4.0).ceil
    else
      redirect_to new_sessions_path
    end

  end

  def new
  end

  def create
    @user = current_user
    choosen_item = params['choosen_item']
    if choosen_item && !choosen_item.empty?
      choosed_items_ids = choosen_item.to_i
    else
      choosed_items_ids = session[:selected_items]
    end
    eve_items = EveItem.where( :id => choosed_items_ids ).to_a
    eve_item_ids = @user.eve_item_ids
    eve_items.reject!{ |item| eve_item_ids.include?( item.id ) }
    ActiveRecord::Base.transaction do
      @user.eve_items << eve_items
      @user.update_attribute(:last_changes_in_choices,Time.now)
    end
    redirect_to edit_choose_items_path
  end

  def update
    @user = current_user
    ActiveRecord::Base.transaction do
      @user.eve_item_ids = params['items_to_keep']
      @user.update_attribute(:last_changes_in_choices,Time.now)
    end
    redirect_to edit_choose_items_path
  end

  def autocomplete_eve_item_name_lowcase
    term = params[:term]
    items = EveItem.where('LOWER(name_lowcase) LIKE ?', "%#{term}%").order(:name_lowcase).all.limit(10)
    session[:selected_items]=items.map{ |e| e.id }
    render :json => items.map { |items| {:id => items.id, :label => items.name, :value => items.name} }
  end

end
