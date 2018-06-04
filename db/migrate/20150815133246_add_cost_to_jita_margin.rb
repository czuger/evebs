class AddCostToJitaMargin < ActiveRecord::Migration[4.2]
  def change
    add_column :jita_margins, :cost, :float
  end
end
