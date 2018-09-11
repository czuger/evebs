module ProductionListsHelper

  def production_list_check_box( item, delete_on_change: false, force_checked: false )

    # item can come from PriceAdvice or ProductionList.
    # So item.id does not refer to a single object type and can be used only as a css id, not an internal db id
    if item.is_a?( PricesAdvice ) || item.is_a?( BuyOrdersAnalyticsResult )
      item = { 'trade_hubs.id' => item.trade_hub_id, 'eve_items.id' => item.eve_item_id, 'id' => item.id }
    elsif item.is_a? PriceAdviceMarginComp
      item = { 'trade_hubs.id' => item.trade_hub_id, 'eve_items.id' => item.item_id, 'id' => item.id }
    elsif item.is_a? EveItem
      item = { 'trade_hubs.id' => @jita.id, 'eve_items.id' => item.id, 'id' => item.id }
    end

    classes = [ :shopping_basket_checkbox ]
    classes << :delete_on_change if delete_on_change

    # p item

    check_box_tag(
        "eve_item_#{item['id']}", item['id'],
        force_checked || @checked_production_list_ids.include?( [ item['trade_hubs.id'], item['eve_items.id'] ] ),
        { class: classes, trade_hub_id: item['trade_hubs.id'], eve_item_id: item['eve_items.id'],
          'data-toggle' => :tooltip, title: 'Uncheck to remove item' }
    )
  end

end
