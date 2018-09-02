class RemoveHistoryVolumeFromPricesAdvices < ActiveRecord::Migration[5.2]
  def change
    drop_view :price_advice_margin_comps
    remove_column :prices_advices, :history_volume
  end
end
