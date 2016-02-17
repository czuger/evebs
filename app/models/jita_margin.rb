class JitaMargin < ActiveRecord::Base

  belongs_to :eve_item

  def self.compute_margins

    jita = TradeHub.find_by_eve_system_id( Component::JITA_EVE_SYSTEM_ID )
    items_processed = 0
    EveItem.find_each do |item|

      next if item.epic_blueprint

      puts "Computing margin for #{item.name}"

      min_price = MinPrice.find_by_eve_item_id_and_trade_hub_id( item.id, jita.id )

      if min_price && item.blueprint && item.cost
        bp = item.blueprint
        # puts item.inspect
        batch_size = item.full_batch_size
        unit_cost = item.cost / bp.prod_qtt
        margin = min_price.min_price - unit_cost
        margin_percent = ( min_price.min_price / unit_cost ) - 1

        cplma = CrestPricesLastMonthAverage.find_by_region_id_and_eve_item_id( jita.region_id, item.cpp_eve_item_id )
        sum_volume = cplma ? cplma.volume_sum : -1

        jita_margin = JitaMargin.find_or_create_by!( eve_item_id: item.id )
        jita_margin.update_attributes( margin: margin * batch_size,
          jita_min_price: min_price.min_price, cost: unit_cost,
          margin_percent: margin_percent, mens_volume: sum_volume, batch_size: batch_size )

        items_processed += 1
      end
    end
    puts "#{items_processed} items processed"
  end
end
