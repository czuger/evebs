class UpdatePriceAdviceMarginCompsToVersion3 < ActiveRecord::Migration[5.2]
  def change
    update_view :price_advice_margin_comps, version: 3, revert_to_version: 2
  end
end
