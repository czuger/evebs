class AddMarginPercentToJitaMargin < ActiveRecord::Migration
  def change
    add_column :jita_margins, :margin_percent, :float
  end
end
