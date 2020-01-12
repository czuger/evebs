class ListItemsController < ApplicationController

  before_action :require_logged_in!, except: [ :all_items_list, :show ]
  before_action :set_user, :set_small_screen

  include Modules::CheckedProductionListIds

  def show
    @title = 'Types list'
    # items_list false
    set_current_group

    @item_ids = @user.eve_item_ids.uniq.to_set if @user
    @breadcrumb = @current_group.breadcrumb( view_context )
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

  private

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
			# @current_group is used for bc generation only.
      @current_group = Misc::BreadcrumbRoot.new
    end
  end

end
