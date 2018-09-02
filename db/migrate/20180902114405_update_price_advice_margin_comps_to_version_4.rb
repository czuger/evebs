class UpdatePriceAdviceMarginCompsToVersion4 < ActiveRecord::Migration[5.2]
  def change
    create_view :price_advice_margin_comps, version: 4
  end
end
