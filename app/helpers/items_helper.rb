module ItemsHelper

  def print_total_cost_for_items( item )
    single_cost = item.cost
    single_cost ? "(#{print_isk( single_cost )})" : 'N/A'
  end

  def breadcrumb
    unless @breadcrumb
      @current_group = @item.market_group if @item

      if @current_group
        @breadcrumb = [ OpenStruct.new( name: 'Root', group_id: nil ) ]
        @breadcrumb += @current_group.ancestors.reverse.map{ |e| OpenStruct.new( name: e.name, group_id: e.id ) }
        @breadcrumb << OpenStruct.new( name: @current_group.name, group_id: @current_group.id )
      end

    end
    @breadcrumb
  end

end
