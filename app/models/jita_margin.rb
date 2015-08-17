class JitaMargin < ActiveRecord::Base

  belongs_to :eve_item

  def self.compute_margins

    jita = TradeHub.find_by_eve_system_id( Component::JITA_EVE_SYSTEM_ID )
    EveItem.find_each do |item|

      min_price = MinPrice.find_by_eve_item_id_and_trade_hub_id( item.id, jita.id )

      if min_price && item.blueprint && item.cost
        # puts item.inspect
        unit_cost = item.cost / item.blueprint.prod_qtt
        margin = min_price.min_price - unit_cost
        margin_percent = min_price.min_price * 100 / unit_cost

        jita_margin = JitaMargin.find_or_create_by!( eve_item_id: item.id )
        jita_margin.update_attributes( margin: margin, jita_min_price: min_price.min_price, cost: unit_cost,
          margin_percent: margin_percent )
      end

    end

  end

end
