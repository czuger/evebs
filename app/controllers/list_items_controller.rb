class ListItemsController < ApplicationController

  before_action :require_logged_in!, except: [ :all_items_list, :show ]
  before_action :set_user, :set_small_screen

  include Modules::CheckedProductionListIds

  def show
    @title = 'Types list'
    # items_list false
    set_current_group

    @item_ids = @user.eve_item_ids.uniq.to_set if @user
  end

  # def all_items_list
  #   @title = 'All items list'
  #   # items_list false
  #   set_current_group
  #   @item_ids = []
  # end
	#
  # def my_items_list
  #   @title = 'My items list'
  #   # items_list true
  #   set_current_group
	#
  #   @my_items = true
  # end

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
    clear_user_list
    redirect_to saved_list_list_items_path, notice: 'List cleared successfully'
  end

  # def all
  #   ActiveRecord::Base.transaction do
  #     clear_user_list
  #
  #     EveItem.where.not( blueprint_id: nil ).where( faction: false ).pluck( :id ).in_groups_of( 500 ).each do |g|
  #       links = []
  #       g.each do |eve_item_id|
  #         links << EveItemsUser.new( user_id: @user.id, eve_item_id: eve_item_id, )
  #       end
  #       EveItemsUser.import( links )
  #     end
  #   end
  #
  #   redirect_to saved_list_list_items_path, notice: 'All items are now selected'
  # end

  def save
    @saved_list = EveItemsSavedList.new( user: @user, description: params[:description], saved_ids: @user.eve_item_ids )
    if @saved_list.save
      redirect_to saved_list_list_items_path, notice: 'List saved successfully'
    else
      render :saved_list
    end
  end

  def restore
    saved_list = @user.eve_items_saved_lists.find( params[:saved_list_id] )

    ActiveRecord::Base.transaction do
      clear_user_list

      saved_list&.saved_ids&.in_groups_of( 500 ).each do |g|
        links = []
        g.each do |eve_item_id|
          links << EveItemsUser.new( user_id: @user.id, eve_item_id: eve_item_id, )
        end
        EveItemsUser.import( links )
      end
    end

    redirect_to saved_list_list_items_path, notice: 'List successfully restored'
  end

  def saved_list
    @title = 'My items sets'
    @saved_lists = @user.eve_items_saved_lists.paginate(:page => params[:page], :per_page => 20 )
  end

  private

  def clear_user_list
    EveItemsUser.where( user_id: @user ).delete_all
  end

  def items_list( my_items_only )
    @user = current_user
    @jita = TradeHub.find_by_eve_system_id( 30000142 )
    raise 'Unable to find Jita' unless @jita

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

  def set_current_group
    if params[:group_id]
      @current_group = MarketGroup.find( params[:group_id].to_i )
      if @current_group.leaf?
        @items = @current_group.eve_items.order( 'faction, name' )
        # @items = @items.
      else
        @groups = @current_group.children.order( :name )
      end
    else
      @groups = MarketGroup.roots.order( :name )
    end
  end

end
