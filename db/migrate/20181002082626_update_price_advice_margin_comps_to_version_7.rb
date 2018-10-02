class UpdatePriceAdviceMarginCompsToVersion7 < ActiveRecord::Migration[5.2]
  def change
    update_view :price_advice_margin_comps, version: 7, revert_to_version: 6
  end
end
