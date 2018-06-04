class EveSystemIdNameInnerNotNullOnTradeHub < ActiveRecord::Migration[4.2]
  def change
    change_column_null :trade_hubs, :eve_system_id, false
    change_column_null :trade_hubs, :name, false
    change_column_null :trade_hubs, :inner, false
  end
end
