class MinPrice < ActiveRecord::Base

  belongs_to :eve_item
  belongs_to :trade_hub

  def self.get_best_min_prices

    @prices_array = []

    MinPrice.all.each do |min_price_item|
      if min_price_item.eve_item.cost
        #pp min_price_item
        blueprint = min_price_item.eve_item.blueprint
        batch_size = blueprint.nb_runs*blueprint.prod_qtt
        batch_cost = min_price_item.eve_item.cost*blueprint.nb_runs
        batch_sell_price = min_price_item.min_price*batch_size
        benef = batch_sell_price - batch_cost
        #pp batch_cost
        benef_pcent = ((batch_sell_price*100) / batch_cost).round(0)-100
        @prices_array << {
          trade_hub: min_price_item.trade_hub.name,
          eve_item: min_price_item.eve_item.name,
          min_price: min_price_item.min_price.round(1),
          cost: (min_price_item.eve_item.cost/blueprint.prod_qtt).round(1),
          benef: benef,
          benef_pcent: benef_pcent,
          batch_size: batch_size
        }
      end
    end

    @prices_array.sort_by!{ |e| e[:benef] }
    @prices_array.last( 10 )
  end
end

