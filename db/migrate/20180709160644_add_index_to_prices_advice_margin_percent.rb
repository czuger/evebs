class AddIndexToPricesAdviceMarginPercent < ActiveRecord::Migration[5.2]
  def change
    add_index :prices_advices, :margin_percent
  end
end
