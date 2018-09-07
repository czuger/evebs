class UpdatePriceAdviceMarginCompsToVersion6 < ActiveRecord::Migration[5.2]
  def change
    update_view :price_advice_margin_comps, version: 6, revert_to_version: 5
  end
end
