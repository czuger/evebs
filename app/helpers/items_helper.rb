module ItemsHelper

  def print_total_cost_for_items( item )
    single_cost = item.prices_advices.first
    return 'N/A' unless single_cost
    "( #{print_isk( single_cost.single_unit_cost )})"
  end

end
