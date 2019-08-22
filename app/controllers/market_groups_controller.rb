class MarketGroupsController < ApplicationController
  def index
    if params[:group_id]
      group = MarketGroup.find( params[:group_id].to_i )
      if group.leaf?
        @groups = group.eve_items
      else
        @groups = group.children
      end

      @breadcrumb = group.ancestors.reverse
    else
      @groups = MarketGroup.roots
    end
  end
end
