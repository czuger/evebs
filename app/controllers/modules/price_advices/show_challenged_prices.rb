module Modules::PriceAdvices::ShowChallengedPrices

  def show_challenged_prices

    @user = current_user
    @print_change_warning=print_change_warning

    @trade_orders = @user.trade_orders.includes( { eve_item: :blueprint }, { trade_hub: :region } )
    @compared_prices = []

    @trade_orders.each do |to|
      min_price = PricesMin.find_by_eve_item_id_and_trade_hub_id(to.eve_item_id, to.trade_hub_id )

      min_price = min_price.min_price if min_price

      prod_qtt = to.eve_item.blueprint.prod_qtt
      cost = to.eve_item.cost / prod_qtt
      margin_pcent = ( min_price / cost ) - 1 if cost && min_price

      trade_hub_name = "#{to.trade_hub.name} (#{to.trade_hub.region.name})"

      @compared_prices << {
        trade_hub_name: trade_hub_name, eve_item_name: to.eve_item.name, my_price: to.price,
        min_price: min_price, cost: cost, margin_pcent: margin_pcent, eve_item_id: to.eve_item_id,
        eve_item_cpp_id: to.eve_item.cpp_eve_item_id, trade_hub_cpp_id: to.trade_hub.eve_system_id
      }

      set_trade_hubs( trade_hub_name )
      set_items( to.eve_item.name )

    end

    @compared_prices = @compared_prices.sort_by{ |e| [e[:trade_hub_name], e[:eve_item_name]] }

  end

end