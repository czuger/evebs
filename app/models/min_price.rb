class MinPrice < ActiveRecord::Base

  belongs_to :eve_item
  belongs_to :trade_hub

  include Assert

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

  # Dead code
  #
  # def self.compute_min_price_for_all_items
  #   TradeHub.all.each do |th|
  #     puts "Initializing prices for trade hub : #{th.name}"
  #     EveItem.all.each_slice(200) do |items|
  #       bunch_of_items = items.map{ |e| e.cpp_eve_item_id }
  #       #puts "Initializing prices for items : #{bunch_of_items}"
  #       results = MultiplePriceRetriever.get_prices(th.eve_system_id,bunch_of_items)
  #       #puts results
  #       results.each_pair do |cpp_eve_item_id,min_price|
  #         if min_price
  #           eve_item = EveItem.find_by_cpp_eve_item_id(cpp_eve_item_id)
  #           eve_item.set_min_price_for_system(min_price,th.id)
  #         end
  #       end
  #     end
  #   end
  # end

end

