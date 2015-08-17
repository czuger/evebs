class AddCostToJitaMargin < ActiveRecord::Migration
  def change
    add_column :jita_margins, :cost, :float
  end
end
