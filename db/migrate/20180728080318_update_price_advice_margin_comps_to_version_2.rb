class UpdatePriceAdviceMarginCompsToVersion2 < ActiveRecord::Migration[5.2]
  def change
    update_view :price_advice_margin_comps, version: 2, revert_to_version: 1
  end
end
