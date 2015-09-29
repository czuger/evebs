module PriceAdviceMonthly

  def advice_prices_monthly
    @user = current_user
    @prices_array = []
    @item_count = {}
    @monthly_averages = get_montly_items_averages
    # pp @monthly_averages

    @user.trade_hubs.each do |trade_hub|

      eve_items = @user.eve_items
      if @user.remove_occuped_places
        eve_items = eve_items.where.not( id: trade_hub.get_selling_eve_items_ids( @user ) )
      end

      eve_items.find_each do |eve_item|

        region_item_key = [[trade_hub.region_id],[eve_item.id]]

        blueprint = eve_item.blueprint

        batch_size = blueprint.nb_runs*blueprint.prod_qtt if blueprint

        batch_cost = eve_item.cost*blueprint.nb_runs if eve_item.cost
        item_cost = eve_item.cost/blueprint.prod_qtt if eve_item.cost

        avg_price = volume_avg = order_count_avg = benef = benef_pcent = nil
        if @monthly_averages && @monthly_averages[region_item_key]
          avg_price = @monthly_averages[region_item_key].avg_price_avg
          volume_avg = @monthly_averages[region_item_key].volume_avg
          order_count_avg = @monthly_averages[region_item_key].order_count_avg
        end

        if avg_price && batch_size && batch_cost
          batch_sell_price = avg_price*batch_size
          benef = batch_sell_price - batch_cost
          benef_pcent = ((batch_sell_price*1) / batch_cost)-1
        end

        record_ok_for_user = true
        if @user.min_pcent_for_advice && benef_pcent && benef_pcent < @user.min_pcent_for_advice/100.0
          record_ok_for_user = false
        end
        if @user.min_amount_for_advice && benef_pcent && benef < @user.min_amount_for_advice
          record_ok_for_user = false
        end

        if record_ok_for_user
          price_record = {
            trade_hub: trade_hub.name,
            eve_item: eve_item.name,
            avg_price: avg_price,
            cost: item_cost,
            benef: benef,
            benef_pcent: benef_pcent,
            batch_size: batch_size,
            volume_avg: volume_avg,
            order_count_avg: order_count_avg
          }

          @prices_array << price_record
        end
      end
    end

    @prices_array.sort_by!{ |h| (h[:benef] ? h[:benef] : -Float::INFINITY) }
    @prices_array.reverse!
  end

end