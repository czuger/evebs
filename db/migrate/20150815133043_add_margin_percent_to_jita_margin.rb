class AddMarginPercentToJitaMargin < ActiveRecord::Migration[4.2]
  def change
    add_column :jita_margins, :margin_percent, :float
  end
end
