class AddMarginToPricesAdvice < ActiveRecord::Migration[5.2]
  def change
    add_column :prices_advices, :margin_percent, :float
  end
end
