class AddJitaMinPriceToJitaMargin < ActiveRecord::Migration[4.2]
  def change
    add_column :jita_margins, :jita_min_price, :float
  end
end
