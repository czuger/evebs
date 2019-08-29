class MarketGroupsController < ApplicationController
  def index
    if params[:group_id]
      @current_group = MarketGroup.find( params[:group_id].to_i )
      if @current_group.leaf?
        @groups = @current_group.eve_items
      else
        @groups = @current_group.children
      end

      @breadcrumb = @current_group.ancestors.reverse
    else
      @groups = MarketGroup.roots
    end
  end
end
