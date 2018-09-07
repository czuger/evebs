class CreatePriceAdvicesMinPrices < ActiveRecord::Migration[5.2]
  def change
    create_view :price_advices_min_prices
  end
end
