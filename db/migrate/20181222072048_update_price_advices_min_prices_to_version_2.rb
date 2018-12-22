class UpdatePriceAdvicesMinPricesToVersion2 < ActiveRecord::Migration[5.2]
  def change
    update_view :price_advices_min_prices, version: 2, revert_to_version: 1
  end
end
