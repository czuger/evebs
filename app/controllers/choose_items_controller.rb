require 'pp'

class ChooseItemsController < ApplicationController

  # autocomplete :eve_item, :name_lowcase, full: true

  def index
    @letters = EveItem.select(:first_letter).distinct.sort
  end

  def edit
    @user = User.first
    @items = @user.eve_items.order(:name)
    @per_group_count = (@items.length/4.0).ceil
  end

  def new
  end

  def create
    eve_items = EveItem.where( :id => session[:selected_items] ).to_a
    User.first.eve_items << eve_items
    redirect_to :edit_choose_item
  end

  def update
    User.first.eve_item_ids = params['items_to_keep']
    redirect_to :edit_choose_item
  end

  def autocomplete_eve_item_name_lowcase
    term = params[:term]
    items = EveItem.where('LOWER(name_lowcase) LIKE ?', "%#{term}%").order(:name_lowcase).all.limit(10)
    session[:selected_items]=items.map{ |e| e.id }
    render :json => items.map { |items| {:id => items.id, :label => items.name, :value => items.name} }
  end

end
