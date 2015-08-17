class AddJitaMinPriceToJitaMargin < ActiveRecord::Migration
  def change
    add_column :jita_margins, :jita_min_price, :float
  end
end
