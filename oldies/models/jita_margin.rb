class JitaMargin < ApplicationRecord

  belongs_to :eve_item

  def self.compute_margins

    jita = TradeHub.find_by_eve_system_id(BlueprintComponent::JITA_EVE_SYSTEM_ID )
    items_processed = 0
    EveItem.find_each do |item|

      next if item.epic_blueprint

      # puts "Computing margin for #{item.name}"

      min_price = PricesMin.find_by_eve_item_id_and_trade_hub_id(item.id, jita.id )

      if min_price && item.blueprint && item.cost
        bp = item.blueprint
        # puts item.inspect
        prices_advice = item.prices_advices.first
        if prices_advice
          batch_size = prices_advice.full_batch_size
          unit_cost = prices_advice.cost / prices_advice.prod_qtt
          margin = min_price.min_price - unit_cost
          margin_percent = ( min_price.min_price / unit_cost ) - 1
          final_margin = margin * batch_size

          cplma = CrestPricesLastMonthAverage.find_by_region_id_and_eve_item_id( jita.region_id, item.id )
          sum_volume = cplma ? cplma.volume_sum : -1

          jita_margin = JitaMargin.find_or_create_by!( eve_item_id: item.id )
          jita_margin.update_attributes( margin: final_margin,
            jita_min_price: min_price.min_price, cost: unit_cost,
            margin_percent: margin_percent, mens_volume: sum_volume, batch_size: batch_size )

        end

        items_processed += 1
      end
    end
    puts "#{items_processed} items processed" unless Rails.env == 'test'
  end
end
