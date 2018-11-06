module ItemsHelper

  def print_total_cost_for_items( item )
    single_cost = item.cost
    single_cost ? "(#{print_isk( single_cost )})" : 'N/A'
  end

end
