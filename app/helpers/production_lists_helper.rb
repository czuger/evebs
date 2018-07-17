module ProductionListsHelper

  def print_total_cost_for_items( item )
    single_cost = item.prices_advices.first
    return 'N/A' unless single_cost
    "( #{print_isk( single_cost.single_unit_cost )})"
  end

  def production_list_check_box( item, delete_on_change: false, force_checked: false )

    if item.is_a? PricesAdvice
      item = { id: item.id, trade_hub_id: item.trade_hub_id, eve_item_id: item.eve_item_id }
    end

    classes = [ :shopping_basket_checkbox ]
    classes << :delete_on_change if delete_on_change

    check_box_tag(
        "eve_item_#{item[:id]}", item[:id],
        force_checked || @shopping_basket.include?( item[:id] ),
        { class: :shopping_basket_checkbox, trade_hub_id: item[:trade_hub_id], eve_item_id: item[:eve_item_id],
          'data-toggle' => :tooltip, title: 'Uncheck to remove item' }
    )
  end

end
