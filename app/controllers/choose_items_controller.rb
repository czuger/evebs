require 'pp'

class ChooseItemsController < ApplicationController

  # autocomplete :eve_item, :name_lowcase, full: true

  before_action :require_logged_in!, :log_client_activity

  def edit
    @user = current_user
    @items = @user.eve_items.includes(:market_group).order(:name)
    @groups = {}
    @no_groups = []
    if @items && !@items.empty?
      @items.each do |item|
        market_group = item.market_group
        if market_group
          name = market_group.get_market_group_breadcrumb
          @groups[name] = {} unless @groups.has_key?(name)
          @groups[name][:name] = market_group.get_market_group_breadcrumb
          @groups[name][:items] = [] unless @groups[name].has_key?(:items)
          @groups[name][:items] << item
        else
          @no_groups << item
        end
      end
    end
  end

  def new
    @message = params[:message]
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

    begin
      ActiveRecord::Base.transaction do
        @user.eve_items << eve_items
        @user.update_attribute(:last_changes_in_choices,Time.now)
      end
    rescue ActiveRecord::RecordInvalid => _
      flash.alert = @user.errors
      error = true
    end
    flash.notice = 'Item(s) added successfully' unless error
    redirect_to new_choose_items_path
  end

  def update
    @user = current_user
    begin
      ActiveRecord::Base.transaction do
        if params.has_key?( 'remove_all_items' )
          # Decided to uncheck all items
          @user.eve_item_ids = []
        else
          # We manually unchecked some items
          @user.eve_item_ids = params['items_to_keep']
        end
        @user.update_attribute(:last_changes_in_choices,Time.now)
      end
    rescue ActiveRecord::RecordInvalid => _
      flash.alert = @user.errors
      error = true
    end
    flash.notice = 'Item(s) updated successfully' unless error
    redirect_to edit_choose_items_path
  end

  def autocomplete_eve_item_name_lowcase
    term = params[:term]
    items = EveItem.where('LOWER(name_lowcase) LIKE ?', "%#{term.downcase}%").where(involved_in_blueprint: true).order(:name_lowcase).all.limit(30)
    session[:selected_items]=items.map{ |e| e.id }
    render :json => items.map { |items| {:id => items.id, :label => items.name, :value => items.name} }
  end

end
