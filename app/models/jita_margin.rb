class JitaMargin < ActiveRecord::Base

  belongs_to :eve_item

  def self.compute_margins

    jita = TradeHub.find_by_eve_system_id( Component::JITA_EVE_SYSTEM_ID )
    EveItem.find_each do |item|

      next if item.epic_blueprint

      min_price = MinPrice.find_by_eve_item_id_and_trade_hub_id( item.id, jita.id )

      if min_price && item.blueprint && item.cost
        # puts item.inspect
        unit_cost = item.cost / item.blueprint.prod_qtt
        margin = min_price.min_price - unit_cost
        margin_percent = min_price.min_price / unit_cost
        cplma = CrestPricesLastMonthAverage.find_by_region_id_and_eve_item_id( jita.region_id, item.cpp_eve_item_id )
        sum_volume = cplma ? cplma.volume_sum : -1

        jita_margin = JitaMargin.find_or_create_by!( eve_item_id: item.id )
        jita_margin.update_attributes( margin: margin, jita_min_price: min_price.min_price, cost: unit_cost,
          margin_percent: margin_percent, mens_volume: sum_volume )
      end
    end
  end
end
