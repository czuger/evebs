module ItemsHelper

  def print_total_cost_for_items( item )
    single_cost = item.cost
    single_cost ? "(#{print_isk( single_cost )})" : 'N/A'
  end

  def breadcrumb
    unless @breadcrumb
      @current_group = @item.market_group if @item

      if @current_group
        @breadcrumb = @current_group.ancestors.reverse
        @breadcrumb << @current_group
      end

    end
    @breadcrumb
  end

end
